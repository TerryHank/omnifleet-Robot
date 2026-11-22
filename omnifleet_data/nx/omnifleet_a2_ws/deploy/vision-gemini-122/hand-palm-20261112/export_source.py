"""Read-only source/model snapshot; never dereference Linux symlinks."""
from pathlib import Path
import collections,datetime,fnmatch,hashlib,json,os,re,subprocess,sys,tarfile,io

robot=sys.argv[1]
assert robot in ('126','122')
home=Path.home();ws=home/('omnifleet_ws' if robot=='126' else 'omnifleet_a2_ws')
out=home/('robot_backups' if robot=='126' else 'omnifleet_a2_backups')/'git-source-20261112'
out.mkdir(parents=True,exist_ok=True)
skip_dirs={'.git','node_modules','.venv','venv','.env','.cache','.pytest_cache','__pycache__',
           'build','install','log','logs','Log','MvSdkLog','dist','out','.next','coverage','CMakeFiles',
           'backups','recordings','.webpack'}
skip_suffix={'.pyc','.pyo','.bag','.mcap','.db3','.simplemap','.avi','.mp4','.mov','.webm',
             '.jks','.keystore','.pfx','.p12','.key','.rawlog','.map','.zip','.tar','.tgz','.gz','.7z','.rar','.bz2','.xz'}
skip_names={'.env','id_rsa','id_ed25519','credentials.json','token.json','secrets.json','secrets.yaml'}
findings=[];excluded=[];entries=[];seen=set();mapping=[];counts=collections.Counter()
hard=re.compile(rb'-----BEGIN (?:[A-Z0-9 ]* )?PRIVATE KEY-----[ \t\r\n\\n]+[A-Za-z0-9+/=]{24,}|\b(?:gh[pousr]_[A-Za-z0-9]{28,}|sk-proj-[A-Za-z0-9_-]{40,}|AKIA[A-Z0-9]{16})\b')
literal=re.compile(rb'(?im)\b(?:password|passwd|api_key|access_token|auth_token|client_secret|wifi_password)\b\s*[:=]\s*([\x22\x27])([^\x22\x27\r\n]{6,})\1')

def ignored(path,relative):
    parts=relative.parts
    if path.name in skip_names or path.suffix.lower() in skip_suffix:return 'credential/generated/runtime file'
    if path.suffix=='.nmconnection':return 'network credentials'
    if any(p in skip_dirs for p in parts[:-1]):return 'generated/runtime directory'
    if any(parts[i:i+2]==('.yarn','cache') for i in range(max(0,len(parts)-1))):return 'package-manager cache'
    if any(p.startswith(('log_','build_','install_')) and p not in ('build_scripts',) for p in parts[:-1]):return 'generated tree'
    if any(p.startswith(('hand-palm-','hand-nanotrack-','sync-unified-')) for p in parts[:-1]):return 'diagnostic staging tree'
    return None

def add(archive,path,destination):
    if destination in seen:return
    seen.add(destination)
    try:stat=path.lstat()
    except FileNotFoundError:
        excluded.append(dict(path=destination,reason='source disappeared during read'));return
    info=tarfile.TarInfo(destination);info.mtime=int(stat.st_mtime);info.mode=stat.st_mode&0o777
    if path.is_symlink():
        target=os.readlink(path);info.type=tarfile.SYMTYPE;info.linkname=target;archive.addfile(info)
        entries.append(dict(path=destination,type='symlink',target=target,mode=info.mode));counts['symlinks']+=1;return
    if not path.is_file():return
    if stat.st_size>95*1024**2:raise RuntimeError('Oversize source file: '+destination)
    data=path.read_bytes()
    if b'\0' not in data[:8192]:
        matches=list(hard.finditer(data))
        if matches:
            findings.append(dict(path=destination,category='private-key/access-token marker',lines=[data[:m.start()].count(b'\n')+1 for m in matches]))
            excluded.append(dict(path=destination,reason='private-key/access-token marker'));return
        for match in literal.finditer(data):
            value=match.group(2)
            findings.append(dict(path=destination,category='literal review',line=data[:match.start()].count(b'\n')+1,length=len(value)))
    info.size=len(data);archive.addfile(info,io.BytesIO(data))
    entries.append(dict(path=destination,type='file',size=len(data),sha256=hashlib.sha256(data).hexdigest(),mode=info.mode))
    counts['files']+=1;counts['bytes']+=len(data)

def tree(archive,source,prefix):
    if not source.exists():return
    mapping.append(dict(source=str(source),snapshot=prefix))
    if source.is_file() or source.is_symlink():add(archive,source,prefix);return
    for base,dirs,files in os.walk(source,followlinks=False):
        parent=Path(base)
        kept=[]
        for name in sorted(dirs):
            p=parent/name;relative=p.relative_to(source)
            if name in skip_dirs or ignored(p,relative/'_'):
                excluded.append(dict(path=prefix+'/'+relative.as_posix()+'/',reason='generated/runtime directory'));continue
            if p.is_symlink():add(archive,p,prefix+'/'+relative.as_posix())
            else:kept.append(name)
        dirs[:]=kept
        for name in sorted(files):
            p=parent/name;relative=p.relative_to(source);reason=ignored(p,relative)
            if reason:excluded.append(dict(path=prefix+'/'+relative.as_posix(),reason=reason));continue
            add(archive,p,prefix+'/'+relative.as_posix())

archive_path=out/'source.tar.gz'
with tarfile.open(archive_path,'w:gz',compresslevel=1,dereference=False) as archive:
    tree(archive,ws/'src','src')
    for name in ['README.md','README.workspace.md','AGENTS.md','env.bash','.gitignore','.gitattributes','CUTOVER_CHECKLIST.md']:
        if (ws/name).is_file():tree(archive,ws/name,name)
    if robot=='122':
        for name in ['deploy','firmware','foxglove']:tree(archive,ws/name,name)
    models=home/'omnifleet_data/ml_models/omnifleet_vision/vendor'
    for name in ['mediapipe_tensorrt','nanotrack_v2','yolo26_person_follow']:
        tree(archive,models/name,'models/vision/vendor/'+name)
    web=Path('/opt/foxglove-studio-cn-'+('104' if robot=='126' else '122')+'/site')
    for name in ['vision-follow.html','vision-follow.js']:
        tree(archive,web/name,'web/'+name)
    if robot=='126':
        camera=home/'orbbec345lg-v2.10.6'
        for name in ['rgb1080.py','rgb1080-calibration.json']:
            tree(archive,camera/name,'camera/'+name)
    for directory in [Path('/etc/systemd/system'),home/'.config/systemd/user']:
        if directory.exists():
            for p in sorted(directory.iterdir()):
                if p.name.startswith(('omnifleet','robot-wifi','yahboom')) and (p.is_file() or p.is_symlink() or p.name.endswith('.d')):
                    tree(archive,p,'system/'+str(p).lstrip('/'))
    rules=Path('/etc/udev/rules.d')
    if rules.exists():
        for p in rules.iterdir():
            if any(x in p.name.lower() for x in ['omnifleet','yahboom','orbbec']):tree(archive,p,'system/etc/udev/rules.d/'+p.name)
    stage=(home/'robot_backups/hand-palm-20261112' if robot=='126' else ws/'deploy/vision-gemini-122/hand-palm-20261112')
    for name in ['deployment.json','runtime.json','palm-numeric.json']:
        tree(archive,stage/name,'verification/'+name)
    if robot=='126':
        tree(archive,home/'robot_backups/gesture-motion-20261112/verification-summary.json','verification/gesture-motion-summary.json')

source_git={}
if (ws/'.git').exists():
    for key,args in [('commit',['rev-parse','HEAD']),('branch',['branch','--show-current'])]:
        source_git[key]=subprocess.check_output(['git','-C',str(ws),*args],text=True).strip()
manifest=dict(robot=robot,workspace=str(ws),created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    archive_sha256=hashlib.sha256(archive_path.read_bytes()).hexdigest(),archive_bytes=archive_path.stat().st_size,
    counts=dict(counts),source_git=source_git,mapping=mapping,entries=entries,excluded=excluded,audit_findings=findings,
    excluded_scope='Build/install/log/cache/credentials, recorded camera/video/ROS data and runtime maps; no system image or credential backup.')
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
(out/'audit.json').write_text(json.dumps(findings,indent=2))
print(json.dumps({k:manifest[k] for k in ['robot','archive_sha256','archive_bytes','counts','source_git']},ensure_ascii=False),flush=True)
print('AUDIT_REVIEW_COUNT',len(findings),flush=True)
