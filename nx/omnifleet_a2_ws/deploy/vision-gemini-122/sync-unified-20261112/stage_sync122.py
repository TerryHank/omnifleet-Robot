from pathlib import Path
import hashlib
import json
import shutil
import tarfile

workspace=Path.home()/'omnifleet_a2_ws'
base=workspace/'deploy/vision-gemini-122'
runtime=base/'from-126.4EV8FJM3'
stage=base/'sync-unified-20261112'
source=stage/'source'
source.mkdir(exist_ok=True)

def extract(archive,destination):
    destination.mkdir(parents=True,exist_ok=True)
    with tarfile.open(archive) as bundle:
        for item in bundle.getmembers():
            target=(destination/item.name).resolve()
            assert target.is_relative_to(destination.resolve()),item.name
            assert not item.issym() and not item.islnk(),item.name
        bundle.extractall(destination,filter='data')

extract(stage/'source.tar.gz',source)
extract(stage/'hand-runtime.tar.gz',Path.home()/'omnifleet_ws/.env')

protected=[Path('/etc/omnifleet_a2/robot.env'),base/'split1080/rgb1080-calibration.yaml',
    base/'split1080/gemini_pro_1080.launch.py',workspace/'deploy/chassis-111/firmware.json',
    workspace/'deploy/web-112/server.py']
protected += list((workspace/'src/system/omnifleet_bringup/omnifleet_bringup').glob('*driver*.py'))
manifest={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected if p.is_file()}
(stage/'protected-before.json').write_text(json.dumps(manifest,indent=2))

def edit(path,old,new):
    text=path.read_text();assert text.count(old)==1,(path,old)
    text=text.replace(old,new)
    if path.suffix=='.py':compile(text,str(path),'exec')
    path.write_text(text)

package=source/'src/perception/omnifleet_person_follow/omnifleet_person_follow'
node=package/'node.py'
edit(node,'        self.info = message\n', '''        if self.camera_backend == 'orbbec':
            from copy import deepcopy
            from omnifleet_hikrobot_rgbd.local_frames import native_color_geometry
            geometry, _ = native_color_geometry((message.width,message.height), (message.width,message.height))
            message = deepcopy(message)
            message.k, message.p, message.d = geometry['k'], geometry['p'], geometry['d']
        self.info = message
''')
edit(node,"                    if message.encoding == 'rgb8':\n                        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)",
     "                    if message.encoding == 'rgb8':\n                        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)\n                    if self.camera_backend == 'orbbec':\n                        image = rectify_native_color(image)")

local=runtime/'vendor/home/iecme/omnifleet_ws/src/sensing/omnifleet_hikrobot_rgbd/omnifleet_hikrobot_rgbd/local_frames.py'
shutil.copy2(local,stage/'local_frames.py')
edit(stage/'local_frames.py',"    path = Path.home() / 'orbbec345lg-v2.10.6/rgb1080-calibration.json'\n    color = json.loads(path.read_text())['color']",'''    calibration = os.environ.get('OMNIFLEET_COLOR_CALIBRATION')
    if calibration:
        import yaml
        data = yaml.safe_load(Path(calibration).read_text())
        color = dict(width=data['image_width'],height=data['image_height'],
                     k=data['camera_matrix']['data'],d=data['distortion_coefficients']['data'],
                     distortion_model=data.get('distortion_model','rational_polynomial'))
    else:
        path = Path.home() / 'orbbec345lg-v2.10.6/rgb1080-calibration.json'
        color = json.loads(path.read_text())['color']''')

shutil.copy2(runtime/'manager.py',stage/'manager.py')
edit(stage/'manager.py', 'BODY_CONTROL = "/body_tracking_104/horizon_tracking_RobotCmdVel"',
     '''BODY_CONTROL = "/body_tracking_104/horizon_tracking_RobotCmdVel"
os.environ['OMNIFLEET_COLOR_CALIBRATION'] = str(ROOT.parent/'split1080/rgb1080-calibration.yaml')
sys.path.insert(0,str(SOURCE/'src/sensing/omnifleet_hikrobot_rgbd'))''')
edit(stage/'manager.py','''        if scale < 1:
            image = cv2.resize(image, (round(width * scale), round(height * scale)),
                               interpolation=cv2.INTER_AREA)''','''        if self.active_case == PERSON_CASE:
            from omnifleet_hikrobot_rgbd.local_frames import rectify_native_color
            image = rectify_native_color(image,(round(width*scale),round(height*scale)))
        elif scale < 1:
            image = cv2.resize(image, (round(width * scale), round(height * scale)),
                               interpolation=cv2.INTER_AREA)''')
print('STAGED',stage,'protected files',len(manifest))
