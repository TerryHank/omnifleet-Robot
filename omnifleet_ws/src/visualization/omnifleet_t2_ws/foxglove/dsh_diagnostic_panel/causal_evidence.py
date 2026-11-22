"""Bounded read-only navigation evidence, with explicit chronology and scope."""
import copy,json,re,subprocess,time,hashlib,ast,os
from pathlib import Path

RELEVANT=re.compile(r'Continuous route stopped|连续段初始化|开始连续路径跟踪|初始化超时|TF年龄|开始前检查|提交第|导航执行中|连续导航失败|停止路线|相关请求已结束|整条路线完成|停稳|stale localization|worker.*busy|CRITICAL FAILURE|process has died|Closing transport|timestamp.*reject|Message Filter dropping',re.I)

def collect_evidence(robot,live_events=()):
    events=[];gaps=[];now=time.time()
    try:
        result=subprocess.run(['journalctl','-b','-u','omnifleet-local-navigation.service','--since','-2 hours','-n','1000','-o','json','--no-pager'],capture_output=True,text=True,timeout=4)
        if result.returncode:raise RuntimeError('journal unavailable')
        for line in result.stdout.splitlines():
            row=json.loads(line);message=row.get('MESSAGE','')
            if not isinstance(message,str) or not RELEVANT.search(message):continue
            match=re.search(r'\[(\d{10}\.\d+)\]',message)
            stamp=float(match[1]) if match else int(row['__REALTIME_TIMESTAMP'])/1e6
            events.append({'time':stamp,'source':'local_navigation journal','message':message[:850]})
    except Exception as error:gaps.append('journal: '+str(error)[:120])
    # Read the current managed launch log, without executing anything from it.
    directory=Path.home()/'.local/share/omnifleet_t2/navigation-stack'
    try:
        candidates=sorted(directory.glob('*.log'),key=lambda p:p.stat().st_mtime,reverse=True)
        if candidates:
            with candidates[0].open('rb') as f:
                f.seek(0,2);size=f.tell();f.seek(max(0,size-600000));text=f.read().decode('utf8',errors='replace')
            for line in text.splitlines():
                match=re.search(r'\[(\d{10}\.\d+)\]',line)
                if match and now-7200<=float(match[1])<=now+1 and RELEVANT.search(line):
                    events.append({'time':float(match[1]),'source':'active MOLA/Nav2 launch log','message':line[:850]})
    except Exception as error:gaps.append('launch log: '+str(error)[:120])
    events.extend(dict(e) for e in live_events if now-e.get('time',0)<7200)
    events=sorted(events,key=lambda e:e['time'])[-80:]
    for i,event in enumerate(events,1):event['id']='E'+str(i).zfill(3)
    checks=[]
    sources=[('/home/iecme/omnifleet_ws/src/control/omnifleet_local_navigation/omnifleet_local_navigation/route_execution.py',
              ['    def on_tf(', '    def tick(']),
             ('/home/iecme/omnifleet_ws/src/planning/omnifleet_planner/src/continuous_route_control.hpp',
              ['      transform=tf_->lookupTransform'])]
    for filename,anchors in sources:
        try:
            text=Path(filename).read_text()
            excerpts=[text[text.index(a):text.index(a)+850] for a in anchors if a in text]
            if filename.endswith('.py'):
                excerpts=[ast.get_source_segment(text,n) for n in ast.walk(ast.parse(text)) if isinstance(n,ast.FunctionDef) and n.name in ('on_tf','tick')]
            checks.append({'file':filename,'sha256':hashlib.sha256(text.encode()).hexdigest(),'excerpts':excerpts})
        except OSError:gaps.append('source not available: '+filename)
    experiments=[]
    folder=Path.home()/'.local/share/omnifleet_t2/navigation-experiments'
    if folder.exists():
        for p in sorted(folder.glob('*.json'),key=lambda p:p.stat().st_mtime,reverse=True)[:3]:
            try:
                report=json.loads(p.read_text())
                if report.get('robot_id')==robot and 0<=now-report.get('captured_at',0)<7200:experiments.append(report)
            except (OSError,ValueError,TypeError):pass
    return {'robot_id':robot,'captured_at':now,'lookback_seconds':7200,'events':events,'experiment_reports':experiments,'collection_gaps':gaps,'source_checks':checks,
            'interpretation':'事件先后只证明时间顺序；TF过期是取消触发原因，不自动证明Zenoh、传感器或MOLA计算是底层根因。',
            'verified_guard_scope':'实际路径跟踪阶段，单点和多点都执行真实定位数据年龄500ms上限。自定义连续段初始化时底盘输出关闭，等待定位连续稳定2秒，最多5秒；这不是放宽运行期门限。初始化失败、行驶期定位失败和路径障碍失败应分开判断。',
            'chain_to_check':['目标提交','整条路线预检','连续段/单点执行','MOLA位姿与TF新鲜度','Nav2规划/控制状态','输出速度','取消确认与停稳']}

def prepare_scope(question,snapshot):
    result=copy.deepcopy(snapshot);owner=result.get('parameter_owner') or os.environ.get('OMNIFLEET_ROBOT_ID', '')
    fleet=bool(re.search(r'双车|两车协同|多机|编队|协同调度',question)) and not re.search(r'单车|本车|只对|仅对',question)
    result['diagnosis_scope']={'mode':'fleet' if fleet else 'local','robot_id':owner,
        'rule':'本地单点/多点只依赖本车定位、地图、Nav2和底盘；另一辆车未就绪、共享地图未对齐或协同运动未开启，不能据此断言本地任务失败。'}
    if not fleet and 'fleet' in result:
        robots=result['fleet'].get('robots',{})
        local=robots.get(owner,{})
        result['fleet']={'role':'optional coordination context, not a local navigation prerequisite',
                         'robots':{owner:{k:v for k,v in local.items() if k not in ('runtime_parameters','shared_map')}}}
    return result

def validate_chain(result,snapshot):
    evidence=snapshot.get('causal_evidence',{})
    chain=result.get('causal_chain',[])
    if not isinstance(chain,list):raise ValueError('invalid causal chain')
    if not chain:return []
    if len(chain)>8:raise ValueError('causal chain too long')
    allowed={e['id'] for e in evidence.get('events',[])}
    for link in chain:
        if not isinstance(link,dict) or not link.get('cause') or not link.get('effect'):raise ValueError('invalid causal link')
        ids=link.get('evidence_ids',[])
        if not isinstance(ids,list) or not set(ids)<=allowed:raise ValueError('unsupported evidence reference')
        if link.get('confidence') not in ('confirmed','hypothesis'):raise ValueError('missing causal confidence')
        if link['confidence']=='confirmed' and not ids:raise ValueError('confirmed cause needs evidence')
    return chain

def extract_result(text):
    """Accept a terminal JSON answer after harness narration, never show the narration."""
    decoder=json.JSONDecoder()
    try:return json.loads(text)
    except ValueError:pass
    for index,ch in enumerate(text):
        if ch!='{':continue
        try:result,end=decoder.raw_decode(text,index)
        except ValueError:continue
        if isinstance(result,dict) and isinstance(result.get('answer'),str) and text[end:].strip() in ('','```'):
            return result
    raise ValueError('no complete terminal diagnostic JSON')
