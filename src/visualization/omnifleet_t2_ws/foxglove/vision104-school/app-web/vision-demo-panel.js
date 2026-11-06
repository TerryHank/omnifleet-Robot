(function (root) {
  'use strict';
  const CONTROL = '/vision/demo/control', STATUS = '/vision/demo/status';
  const RGB = '/camera/color/image_raw/compressed';
  const sharedRgb=document.createElement('img');
  sharedRgb.alt='104 实时 RGB 图像';
  sharedRgb.draggable=false;
  sharedRgb.dataset.ui='kcfPreview';
  sharedRgb.hidden=true;
  sharedRgb.onload=()=>{
    sharedRgb.frameStamp=sharedRgb.pendingStamp;
    sharedRgb.hidden=false;
    sharedRgb.dispatchEvent(new Event('rgb-frame'));
  };
  function updateRgb(message) {
    const stamp=message.header?.stamp;
    const url=URL.createObjectURL(new Blob([message.data],{type:'image/jpeg'}));
    const old=sharedRgb.src;
    sharedRgb.pendingStamp=stamp?Number(stamp.sec)+Number(stamp.nanosec??stamp.nsec??0)*1e-9:0;
    sharedRgb.src=url;
    if(old)URL.revokeObjectURL(old);
  }
  const WAYPOINTS='/omnifleet_t2/waypoints';
  const SINGLE_NAV='04_10_single_navigation', MULTI_NAV='04_11_multi_navigation';
  const navigationView={"cameraState":{"perspective":true,"distance":11.080332409825553,"phi":15.727246451571581,"thetaOffset":58.835970458807594,"targetOffset":[-0.311205057928774,-1.7857851912596798,-3.4226454025779445e-16],"target":[0,0,0],"targetOrientation":[0,0,0,1],"fovy":45,"near":0.1,"far":5000},"followMode":"follow-pose","followTf":"map","scene":{"transforms":{"showLabel":false,"axisScale":0.5,"lineWidth":0,"enablePreloading":true},"meshUpAxis":"z_up","backgroundColor":"#303030"},"transforms":{"frame:map":{"visible":true}},"topics":{"/map":{"visible":true,"colorMode":"custom","minColor":"#cbd9e533","maxColor":"#203e5899","unknownColor":"#ffffff00","fallbackColor":"#ff00ffff","frameLocked":false},"/plan":{"visible":true,"color":"#99999988","lineWidth":0.015},"/local_plan":{"visible":true,"color":"#ff00cc","lineWidth":0.055},"/robot_description":{"visible":true},"/goal_pose":{"visible":true},"/omnifleet_t2/waypoints/add_pose":{"visible":true},"/omnifleet_t2/waypoints/markers":{"visible":true},"/omnifleet_t2/waypoints/path":{"visible":true,"color":"#4499ffaa","lineWidth":0.035},"/omnifleet_t2/waypoints/active_path":{"visible":true,"color":"#00ff66","lineWidth":0.065},"/navigation/deskewed_points":{"visible":false,"pointSize":1,"pointShape":"circle","colorMode":"colormap","colorField":"intensity","colorMap":"turbo","decayTime":0},"/navigation/height_filtered_points":{"visible":false,"pointSize":1.5,"pointShape":"circle","colorMode":"colormap","colorField":"z","colorMap":"turbo","decayTime":0},"/visualization/slam_points_below_1m":{"visible":true,"colorMode":"flat","flatColor":"#ffffffff","pointSize":0.5,"pointShape":"circle","decayTime":0,"frameLocked":true,"colorField":"z"},"/visualization/local_obstacle_points":{"visible":true,"pointSize":1.5,"colorMode":"colormap","colorField":"z","colorMap":"turbo","minValue":0,"maxValue":2,"pointShape":"circle","decayTime":0}},"layers":{"requiredSensorsGrid":{"layerId":"foxglove.Grid","visible":true,"frameLocked":true,"label":"odom 地面网格","frameId":"map","size":20,"divisions":20,"lineWidth":0.5,"color":"#68686855","position":[0,0,0],"rotation":[0,0,0]},"omnifleetT2RobotModel":{"layerId":"foxglove.Urdf","visible":true,"frameLocked":true,"label":"104 履带底盘","instanceId":"omnifleetT2RobotModel","sourceType":"url","framePrefix":"","displayMode":"visual","fallbackColor":"#9e9e9e","order":1,"url":"data:application/xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIj8+Cjxyb2JvdCBuYW1lPSJvbW5pZmxlZXRfdDIiPgogIDxtYXRlcmlhbCBuYW1lPSJib2R5X2JsdWUiPjxjb2xvciByZ2JhPSIwLjA4IDAuMjIgMC40MiAxLjAiLz48L21hdGVyaWFsPgogIDxtYXRlcmlhbCBuYW1lPSJ0cmFja19kYXJrIj48Y29sb3IgcmdiYT0iMC4wNiAwLjA2IDAuMDYgMS4wIi8+PC9tYXRlcmlhbD4KICA8bWF0ZXJpYWwgbmFtZT0ic2Vuc29yX2dyYXkiPjxjb2xvciByZ2JhPSIwLjM1IDAuMzggMC40MiAxLjAiLz48L21hdGVyaWFsPgogIDxtYXRlcmlhbCBuYW1lPSJjYW1lcmFfYmxhY2siPjxjb2xvciByZ2JhPSIwLjAzIDAuMDMgMC4wMyAxLjAiLz48L21hdGVyaWFsPgoKICA8bGluayBuYW1lPSJiYXNlX2Zvb3RwcmludCIvPgogIDxsaW5rIG5hbWU9ImJhc2VfbGluayI+CiAgICA8dmlzdWFsPgogICAgICA8b3JpZ2luIHh5ej0iMCAwIDAiIHJweT0iMCAwIDAiLz4KICAgICAgPGdlb21ldHJ5Pjxib3ggc2l6ZT0iMC41MCAwLjI5IDAuMDgiLz48L2dlb21ldHJ5PgogICAgICA8bWF0ZXJpYWwgbmFtZT0iYm9keV9ibHVlIi8+CiAgICA8L3Zpc3VhbD4KICAgIDxjb2xsaXNpb24+CiAgICAgIDxvcmlnaW4geHl6PSIwIDAgMC4wOSIgcnB5PSIwIDAgMCIvPgogICAgICA8Z2VvbWV0cnk+PGJveCBzaXplPSIwLjUwIDAuMzcgMC4zMyIvPjwvZ2VvbWV0cnk+CiAgICA8L2NvbGxpc2lvbj4KICAgIDxpbmVydGlhbD4KICAgICAgPG9yaWdpbiB4eXo9IjAgMCAwLjA5IiBycHk9IjAgMCAwIi8+CiAgICAgIDxtYXNzIHZhbHVlPSIxMi4wIi8+CiAgICAgIDxpbmVydGlhIGl4eD0iMC4xNjAiIGl4eT0iMCIgaXh6PSIwIiBpeXk9IjAuMzU5IiBpeXo9IjAiIGl6ej0iMC4zODciLz4KICAgIDwvaW5lcnRpYWw+CiAgPC9saW5rPgogIDxqb2ludCBuYW1lPSJiYXNlX2Zvb3RwcmludF9qb2ludCIgdHlwZT0iZml4ZWQiPgogICAgPHBhcmVudCBsaW5rPSJiYXNlX2xpbmsiLz4KICAgIDxjaGlsZCBsaW5rPSJiYXNlX2Zvb3RwcmludCIvPgogICAgPG9yaWdpbiB4eXo9IjAgMCAtMC4wNzUiIHJweT0iMCAwIDAiLz4KICA8L2pvaW50PgoKICA8bGluayBuYW1lPSJsZWZ0X3RyYWNrX2xpbmsiPgogICAgPHZpc3VhbD48Z2VvbWV0cnk+PGJveCBzaXplPSIwLjUwIDAuMDQgMC4wOCIvPjwvZ2VvbWV0cnk+PG1hdGVyaWFsIG5hbWU9InRyYWNrX2RhcmsiLz48L3Zpc3VhbD4KICAgIDxjb2xsaXNpb24+PGdlb21ldHJ5Pjxib3ggc2l6ZT0iMC41MCAwLjA0IDAuMDgiLz48L2dlb21ldHJ5PjwvY29sbGlzaW9uPgogIDwvbGluaz4KICA8am9pbnQgbmFtZT0ibGVmdF90cmFja19qb2ludCIgdHlwZT0iZml4ZWQiPgogICAgPHBhcmVudCBsaW5rPSJiYXNlX2xpbmsiLz4KICAgIDxjaGlsZCBsaW5rPSJsZWZ0X3RyYWNrX2xpbmsiLz4KICAgIDxvcmlnaW4geHl6PSIwIDAuMTY1IC0wLjAzNSIgcnB5PSIwIDAgMCIvPgogIDwvam9pbnQ+CgogIDxsaW5rIG5hbWU9InJpZ2h0X3RyYWNrX2xpbmsiPgogICAgPHZpc3VhbD48Z2VvbWV0cnk+PGJveCBzaXplPSIwLjUwIDAuMDQgMC4wOCIvPjwvZ2VvbWV0cnk+PG1hdGVyaWFsIG5hbWU9InRyYWNrX2RhcmsiLz48L3Zpc3VhbD4KICAgIDxjb2xsaXNpb24+PGdlb21ldHJ5Pjxib3ggc2l6ZT0iMC41MCAwLjA0IDAuMDgiLz48L2dlb21ldHJ5PjwvY29sbGlzaW9uPgogIDwvbGluaz4KICA8am9pbnQgbmFtZT0icmlnaHRfdHJhY2tfam9pbnQiIHR5cGU9ImZpeGVkIj4KICAgIDxwYXJlbnQgbGluaz0iYmFzZV9saW5rIi8+CiAgICA8Y2hpbGQgbGluaz0icmlnaHRfdHJhY2tfbGluayIvPgogICAgPG9yaWdpbiB4eXo9IjAgLTAuMTY1IC0wLjAzNSIgcnB5PSIwIDAgMCIvPgogIDwvam9pbnQ+CgogIDxsaW5rIG5hbWU9InNlbnNvcl9tYXN0X2xpbmsiPgogICAgPHZpc3VhbD4KICAgICAgPG9yaWdpbiB4eXo9IjAgMCAwLjA1NSIgcnB5PSIwIDAgMCIvPgogICAgICA8Z2VvbWV0cnk+PGN5bGluZGVyIHJhZGl1cz0iMC4wMTIiIGxlbmd0aD0iMC4xMSIvPjwvZ2VvbWV0cnk+CiAgICAgIDxtYXRlcmlhbCBuYW1lPSJzZW5zb3JfZ3JheSIvPgogICAgPC92aXN1YWw+CiAgPC9saW5rPgogIDxqb2ludCBuYW1lPSJzZW5zb3JfbWFzdF9qb2ludCIgdHlwZT0iZml4ZWQiPgogICAgPHBhcmVudCBsaW5rPSJiYXNlX2xpbmsiLz4KICAgIDxjaGlsZCBsaW5rPSJzZW5zb3JfbWFzdF9saW5rIi8+CiAgICA8b3JpZ2luIHh5ej0iMC4wMiAwIDAuMDQiIHJweT0iMCAwIDAiLz4KICA8L2pvaW50PgoKICA8bGluayBuYW1lPSJyc2xpZGFyIj4KICAgIDx2aXN1YWw+CiAgICAgIDxvcmlnaW4geHl6PSIwIDAgMC4wMyIgcnB5PSIwIDAgMCIvPgogICAgICA8Z2VvbWV0cnk+PGN5bGluZGVyIHJhZGl1cz0iMC4wNDUiIGxlbmd0aD0iMC4wNiIvPjwvZ2VvbWV0cnk+CiAgICAgIDxtYXRlcmlhbCBuYW1lPSJzZW5zb3JfZ3JheSIvPgogICAgPC92aXN1YWw+CiAgPC9saW5rPgogIDxqb2ludCBuYW1lPSJyc2xpZGFyX2pvaW50IiB0eXBlPSJmaXhlZCI+CiAgICA8cGFyZW50IGxpbms9ImJhc2VfbGluayIvPgogICAgPGNoaWxkIGxpbms9InJzbGlkYXIiLz4KICAgIDxvcmlnaW4geHl6PSItMC4wNDEgMCAwLjE1IiBycHk9IjAgMCAwIi8+CiAgPC9qb2ludD4KCiAgPGxpbmsgbmFtZT0iaW11X2xpbmsiLz4KICA8am9pbnQgbmFtZT0iaW11X2pvaW50IiB0eXBlPSJmaXhlZCI+CiAgICA8cGFyZW50IGxpbms9ImJhc2VfbGluayIvPgogICAgPGNoaWxkIGxpbms9ImltdV9saW5rIi8+CiAgICA8b3JpZ2luIHh5ej0iMCAwIDAiIHJweT0iMCAwIDAiLz4KICA8L2pvaW50PgoKICA8bGluayBuYW1lPSJjYW1lcmFfbGluayI+CiAgICA8dmlzdWFsPgogICAgICA8Z2VvbWV0cnk+PGJveCBzaXplPSIwLjA3IDAuMDI1IDAuMDI4Ii8+PC9nZW9tZXRyeT4KICAgICAgPG1hdGVyaWFsIG5hbWU9ImNhbWVyYV9ibGFjayIvPgogICAgPC92aXN1YWw+CiAgPC9saW5rPgogIDxqb2ludCBuYW1lPSJjYW1lcmFfam9pbnQiIHR5cGU9ImZpeGVkIj4KICAgIDxwYXJlbnQgbGluaz0icnNsaWRhciIvPgogICAgPGNoaWxkIGxpbms9ImNhbWVyYV9saW5rIi8+CiAgICA8b3JpZ2luIHh5ej0iMC4wNSAwIDAiIHJweT0iMCAwIDAiLz4KICA8L2pvaW50Pgo8L3JvYm90Pgo="}},"publish":{"type":"pose","poseTopic":"/goal_pose","pointTopic":"/clicked_point","poseEstimateTopic":"/initialpose","poseEstimateXDeviation":0.5,"poseEstimateYDeviation":0.5,"poseEstimateThetaDeviation":0.26179939},"imageMode":{},"foxglovePanelTitle":"车辆导航"};
  const COLOR_PICK = '/vision/color/pick';
  const CAMERA_CONTROL='/camera/rgbd/control', CAMERA_STATUS='/camera/rgbd/status';
  const FOLLOW_CONTROL='/vision/person_follow/control';
  const KCF_ROI='/omnifleet_vision/kcf/roi';
  const PANEL = 'local.omnifleet-vision.demo!functional-control';
  const NAV = 'local.omnifleet-113-panels.nav2-hot-params-panel!vision104Navigation';
  const TABS = 'Tab!vision104Controls';
  const phases = {IDLE:'未启动',STARTING:'启动中',RUNNING:'运行中',NAVIGATION:'导航模式',STOPPING:'停止中',STOPPED:'已停止',COMPLETED:'进程已结束',ERROR:'错误'};
  const viewLabels = {result:'功能结果图 · Image',rgb:'RGB 对照 · Image',gray:'灰度深度 · Image',goal:'导航候选 · 3D',data:'功能数据 · RawMessages'};

  function initPanel(context) {
    const removedCases = new Set(['02_04_color','04_03_lane_project','04_04_object_navigation','04_05_multimodal_avoidance','04_02_human_object_follow','04_08_gesture_person_follow']);
    const catalog = root.OMNIFLEET_VISION_CASES.filter(item => !removedCases.has(item.id));
    for(const [id,title,guide] of [
      [SINGLE_NAV,'04.10 单点导航','在右侧 3D 用「发布位姿」拖出目标位置与朝向，松开后直接执行单点导航。'],
      [MULTI_NAV,'04.11 多点导航','在右侧 3D 用「发布位姿」逐个录入航点，再点「开始整条路线」。'],
    ])catalog.push({id,title,guide,ui:{views:['goal'],defaultView:'goal',dataTopic:WAYPOINTS+'/catalog',
      dataTopics:[[WAYPOINTS+'/catalog','航点状态']],focus:'104 雷达点云、地图和导航路径'}});
    const isNavigation=id=>id===SINGLE_NAV||id===MULTI_NAV;
    const tuningSpecs=[
      ['reverse_max_speed','后退速度上限',.25,0,.5,.01,' m/s'],
      ['reverse_p','后退 P',1,0,4,.05,''],
      ['steering_p','转向 P',1.8,0,5,.05,''],
      ['steering_d','转向 D',.35,0,1,.01,''],
      ['steering_max_speed','转向速度上限',.8,0,2,.05,' rad/s'],
      ['derivative_weight','阻尼滤波：当前采样权重',.7,0,1,.05,'']
    ];
    const tuningState=Object.fromEntries(tuningSpecs.map(([name])=>[name,{edited:false,pending:undefined}]));
    const el = document.createElement('div');
    el.className = 'vision-demo';
    el.innerHTML = `<style>
      .vision-demo{height:100%;box-sizing:border-box;overflow:auto;padding:14px;color:#e5edf7;background:#151b25;font:14px/1.5 "Microsoft YaHei",sans-serif}
      .vision-demo h2{font-size:21px;margin:0 0 4px}.vision-demo p{margin:6px 0}.vision-demo small{color:#a9bbcf}
      .vision-demo input,.vision-demo select,.vision-demo textarea{box-sizing:border-box;width:100%;font:inherit;color:#e8edf6;background:#202a39;border:1px solid #43536b;border-radius:5px;padding:7px;margin:4px 0}
      .vision-demo select[data-ui=list]{padding:3px;min-height:160px}.vision-demo option{padding:6px}.vision-demo option:checked{background:#245583}
      .vision-demo button{font:inherit;border:1px solid #4c6585;border-radius:5px;padding:8px;color:white;background:#293f59;cursor:pointer}
      .vision-demo button:disabled{opacity:.55;cursor:default}.vision-demo .vd-row{display:flex;gap:7px}.vision-demo .vd-row>*{flex:1;min-width:0}
      .vision-demo .vd-card{padding:10px;border:1px solid #34455b;border-radius:7px;margin:10px 0}.vision-demo [data-ui=start]{background:#1467ad}.vision-demo [data-ui=stop]{background:#9a343f}
      .vision-demo [data-ui=message]{white-space:pre-wrap;color:#9fd3ff}.vision-demo pre{white-space:pre-wrap;overflow:auto;max-height:240px;font:12px/1.45 Consolas,monospace;color:#c5d6e9}
      .vision-demo [data-ui=logs]{height:180px;max-height:300px;background:#101620;padding:8px}.vision-demo label{display:block;margin:5px 0}.vision-demo details{margin:8px 0}
    </style>
    <h2>视觉功能演示</h2><small>104 远端执行 · Windows 操作界面</small>
    <strong>综合案例</strong><details data-ui=allCases><summary>展开其他视觉案例</summary><div class="vd-row"><select data-ui=group aria-label="功能分组"><option value="">全部 ${catalog.length} 项功能</option><option value="02">识别与测距</option><option value="03">融合与行为</option><option value="04">综合案例</option></select><input data-ui=search aria-label="搜索案例" placeholder="搜索编号或功能"></div></details>
    <select size="8" data-ui=list aria-label="视觉功能列表"></select>
    <div class="vd-row"><button data-ui=previous>上一项</button><button data-ui=next>下一项</button></div>
    <div class="vd-row" style="margin-top:8px"><button data-ui=start>开始 / 重新演示</button><button data-ui=stop>停止当前</button><button data-ui=clearWaypoints hidden>清除航点</button></div>
    <div class="vd-card"><strong data-ui=running>正在读取104状态…</strong><p data-ui=message></p><small data-ui=motion>等待案例运动状态</small><p><button data-ui=reconnect hidden>恢复104数据连接</button></p></div>
    <div class="vd-card" data-ui=followControls><strong data-ui=followMode>人体跟随 · 人物选择</strong><div data-ui=followRunMode></div>
      <div data-ui=bodyMotionControls><button data-ui=bodyMotion disabled>等待底盘跟随状态</button><p data-ui=bodyMotionReply>关闭运动仍保留人物识别和跟踪；开启后按当前手势与锁定状态执行。</p></div>
      <select data-ui=targetId aria-label="跟随人物ID"></select><div class="vd-row"><button data-ui=lockTarget>锁定并跟随所选人物</button><button data-ui=pauseFollow>暂停跟随</button></div><p data-ui=followState></p>
      <details data-ui=tuningControls><summary>跟随控制参数 · 热调节</summary>
        ${tuningSpecs.map(([name,label,value,min,max,step,unit])=>`<label>${label}：<strong data-ui="tuningActual_${name}">等待读回</strong><span class="vd-row"><input data-ui="tuning_${name}" type=range min="${min}" max="${max}" step="${step}" value="${value}" aria-label="${label}滑块"><input data-ui="tuningNumber_${name}" type=number min="${min}" ${name==='derivative_weight'?'max="1"':''} step="${step}" value="${value}" aria-label="${label}数值"></span></label>`).join('')}
        <button data-ui=applyTuning>应用全部控制参数</button><p data-ui=tuningReply></p>
        <small>松开单项滑块或输入后按回车可单项应用。显示值来自控制器实际读回；本次运行生效，重启恢复当前默认参数。滤波权重越大，阻尼响应越快。</small>
      </details>
      <div data-ui=distanceControls><label>跟随目标距离：<strong data-ui=actualDistance>等待读回</strong>
        <span class="vd-row"><input data-ui=followDistance type=range min=0.2 max=3 step=0.05 value=1 aria-label="跟随距离滑块"><input data-ui=followDistanceNumber type=number min=0.2 step=0.05 value=1 aria-label="跟随距离数值"></span></label>
        <button data-ui=applyDistance>应用跟随距离</button><p data-ui=distanceReply></p>
        <small>不要求头或脸。单位：米，底盘中心到人物的水平距离；前进、保持、后退共用此目标。松开滑块或输入后按回车生效；重启沿用上次成功设置的距离，保存在104。</small>
      </div></div>
    <div class="vd-card"><button data-ui=restartSlam>重启 SLAM · 清空当前地图重新建图</button><p data-ui=restartSlamReply>重新建立当前地图，航点需要重新录入。</p><button data-ui=clearMap>清空当前地图</button><small style="display:block">清空当前二维栅格和Nav2代价缓存，暂停人体跟随；保留MOLA定位与已保存地图文件。</small><p data-ui=mapReply></p></div>
    <div class="vd-card" data-ui=hikCamera><strong>深度相机 · 热调节</strong><p data-ui=cameraState>等待相机参数…</p>
      <label>ToF深度曝光模式<select data-ui=exposureMode><option value="DynamicMode">自动曝光（相机原生）</option><option value="SingleMode">手动曝光</option></select></label>
      <label><span data-ui=exposureLabel>自动曝光上限（μs）</span>：<strong data-ui=exposureValue>500 μs</strong><span class="vd-row"><input data-ui=exposure type=range value=500 min=3 max=1400 step=1 style="flex:3" aria-label="深度曝光滑块"><input data-ui=exposureNumber type=number value=500 min=3 max=1400 step=1 style="flex:2" aria-label="深度曝光数值"></span></label>
      <small data-ui=exposureRange>设备范围：3–1400 μs；松开滑块立即应用。</small>
      <label><input data-ui=saveExposure type=checkbox style="width:auto"> 保存为开机参数</label>
      <button data-ui=applyExposure>应用深度曝光</button><p data-ui=cameraReply></p>
      <small>RGB保持自动曝光。深度自动上限500μs可达30FPS；手动550μs及以上为15FPS。相机原生平滑/补洞已启用。</small>
    </div>
    <div class="vd-card" data-ui=geminiCamera hidden><strong>Gemini Pro · RGB-D</strong>
      <p>RGB 640×480 · 硬件D2C配准深度640×480 · 30 FPS采集配置</p>
      <p>RGB可选自动或手动曝光；深度AE不支持。相机原生去噪、补洞开启；灰度预览另加边缘保护平滑和小孔补洞。</p>
      <label>RGB曝光模式<select data-ui=rgbMode aria-label="RGB曝光模式"><option value="keep">保持当前模式</option><option value="auto">自动曝光</option><option value="manual">手动曝光</option></select></label>
      <label>RGB曝光：<strong data-ui=rgbActual>等待读回</strong><span class="vd-row"><input data-ui=rgbExposure type=range min=0.1 max=500 step=0.1 value=5 aria-label="RGB曝光滑块"><input data-ui=rgbExposureNumber type=number min=0.1 max=500 step=0.1 value=5 aria-label="RGB曝光毫秒数值"></span></label>
      <div class="vd-row"><button data-ui=rgbRead>读取RGB曝光</button><button data-ui=rgbApply>应用RGB设置</button></div>
      <small>选择模式立即应用；自动模式由相机调整曝光，不支持自动曝光上限。手动单位ms，范围0.1–500ms；松开滑块或输入后按回车应用。本次运行生效。</small><p data-ui=rgbReply></p>
      <label>深度手动曝光（SDK原始单位）<span class="vd-row"><input data-ui=geminiExposure type=range min=0 max=10000 step=1 value=3000><input data-ui=geminiExposureNumber type=number min=0 max=10000 step=1 value=3000></span></label>
      <div class="vd-row"><button data-ui=geminiRead>读取当前值</button><button data-ui=geminiApply>应用曝光</button></div>
      <small>范围0–10000来自设备SDK；此处调整在本次运行生效。硬件配准毫米深度直接用于测距，滤波图用于预览。</small><p data-ui=geminiReply></p>
    </div>
    <div class="vd-card"><strong data-ui=title></strong><p data-ui=focus></p><p data-ui=guide></p><form data-ui=fields></form>
      <label>主演示区<select data-ui=view aria-label="显示内容"></select></label>
      <label>功能数据<select data-ui=dataTopic aria-label="结果话题"></select></label>
      <p data-ui=frames></p><small data-ui=quality></small>
    </div>
    <details data-ui=resultDetails><summary>当前案例结果数据</summary><pre data-ui=result></pre></details>
    <details><summary>启动命令与话题</summary><pre data-ui=command></pre></details>
    <details open><summary>104 实时日志</summary><pre data-ui=logs>新启动案例的日志会显示在这里。</pre></details>`;
    context.panelElement.append(el);
    const ui = {};
    el.querySelectorAll('[data-ui]').forEach(item => {ui[item.dataset.ui]=item; item.dataset.testid='vision-'+item.dataset.ui;});
    const trackingCases=new Set(['02_05_qr','02_06_apriltag','02_07_kcf','04_01_color_follow','04_09_body_tracking']);
    const caseGroup=item=>trackingCases.has(item.id)?"04":item.id.slice(0,2); const visibleCases=()=>ui.allCases.open?catalog:catalog.filter(item=>caseGroup(item)==="04");
    let selected=context.initialState?.selectedCase||'04_01_color_follow';
    if(!visibleCases().some(item=>item.id===selected))selected='04_01_color_follow';
    let selectedView=context.initialState?.selectedView||'result';
    let dataTopic=context.initialState?.dataTopic;
    const views=JSON.parse(JSON.stringify(context.initialState?.views||{}));
    if(views.gray){views.gray.config.imageMode.imageTopic='/camera/depth/image_gray_filtered/compressed';views.gray.config.foxglovePanelTitle='灰度深度 · 平滑 / 小孔补洞预览';}
    let drafts=context.initialState?.parametersByCase||{}, state, received=0, frames=0, frameAt=0, quality, disposed=false, lastLogs='', listKey='';
    let previewPending=trackingCases.has(selected)||isNavigation(selected),route;
    let distanceEdited=false,pendingDistance,motionRequestId,bodyMotion,bodyPendingMotion,bodyMotionBusy=false;
    let geminiSeen=false;
    let lastFollowDistance=context.initialState?.lastFollowDistance;
    let rgbReadAttempted=false;
    let cameraState, cameraRequest, exposureEdited=false, targetListKey='', officialTros=false;
    const results=new Map();
    const fields=new Map();
    const entry=()=>catalog.find(item=>item.id===selected)||catalog[0];
    const values=()=>Object.fromEntries([...fields].map(([key,input])=>[key,input.value]));
    const save=()=>context.saveState?.({...context.initialState,selectedCase:selected,selectedView,dataTopic,views,lastFollowDistance,parametersByCase:drafts});
    function message(text) {ui.message.textContent=text;}
    function subscribe() {
      context.subscribe([...new Set([STATUS,CAMERA_STATUS,RGB,...(isNavigation(selected)?[WAYPOINTS+'/status']:[]),...(!trackingCases.has(selected)&&selectedView==='result'&&selected!=='02_07_kcf'?[entry().displayTopic||entry().imageTopic]:[]),...entry().ui.dataTopics.map(([topic])=>topic),...(entry().ui.usesDepth?['/camera/rgbd/visualization_status']:[])])].map(topic=>({topic})));
    }
    function syncView() {
      const api=root.foxgloveDemoControl;
      // Native cold starts restore panel configs before the named-layout API.
      const existing=api?.layout?.();
      const current=existing?.data?existing:{data:{configById:{[PANEL]:context.initialState||{}},
        layout:{splitPercentage:30},globalVariables:{},userNodes:{},playbackConfig:{speed:1},version:1}};
      if (!api||!current?.data?.configById?.[PANEL]||!isNavigation(selected)&&!views[selectedView]) return;
      const data=JSON.parse(JSON.stringify(current.data));
      const active=Object.values(views).find(view=>data.configById[view.id]);
      if(active)active.config=data.configById[active.id];
      views.result.config.imageMode.imageTopic=entry().displayTopic||entry().imageTopic;
      views.result.config.foxglovePanelTitle=entry().title+' · 功能结果';
      views.data.config.topicPath=dataTopic;
      views.data.config.foxglovePanelTitle=entry().title+' · '+entry().ui.dataTopics.find(([topic])=>topic===dataTopic)[1];
      const markerKind=selected==='02_05_qr'?'qr':selected==='02_06_apriltag'?'apriltag':undefined;
      const colorFollow=['02_04_color','04_01_color_follow'].includes(selected);
      const target=isNavigation(selected)?{id:'3D!navigation',config:{...navigationView,
        foxglovePanelTitle:entry().title+' · 地图和点云',
        publish:{...navigationView.publish,poseTopic:selected===SINGLE_NAV?'/goal_pose':WAYPOINTS+'/add_pose'}}}:trackingCases.has(selected)&&selectedView==='result'?{id:'local.omnifleet-vision.kcf!interactive-follow',config:{markerKind,followKind:colorFollow?'color':undefined,caseId:selected,foxglovePanelTitle:selected==='04_09_body_tracking'?'人体手势跟随':colorFollow?'颜色点击跟随':markerKind?'二维码 / AprilTag 跟随':'目标物跟随窗口 · NanoTrack/KCF'}}:views[selectedView];
      // The native renderer keeps per-panel state: use a distinct instance when
      // changing case or data topic so old image/topic settings cannot survive.
      target.id=target.id.split('!')[0]+'!case104_'+selected+'_'+selectedView+(selectedView==='data'?'_'+entry().ui.dataTopics.findIndex(([topic])=>topic===dataTopic):'');
      if(target.id.startsWith('Image!'))target.id+='_jpeg';
      data.configById={
        [PANEL]:{...data.configById[PANEL],selectedCase:selected,selectedView,dataTopic,views,lastFollowDistance,parametersByCase:drafts},
        [target.id]:target.config,
      };
      data.layout={direction:'row',first:PANEL,second:target.id,splitPercentage:data.layout.splitPercentage||30};
      if(selected==='04_08_gesture_person_follow'&&views.followMap){
        const map=views.followMap;
        if(current.data.configById[map.id])map.config=current.data.configById[map.id];
        data.configById[map.id]=map.config;
        data.layout.second={direction:'column',first:target.id,second:map.id,splitPercentage:55};
      }
      data.configById[NAV]=current.data.configById[NAV]||context.initialState.navigationConfig;
      data.configById[TABS]={...(current.data.configById[TABS]||{}),activeTabIdx:0,tabs:[
        {title:'视觉案例',layout:PANEL},{title:'104导航永久参数',layout:NAV},
      ]};
      data.layout.first=TABS;
      api.setLayout('104 视觉功能演示',data);
    }
    function showFields() {
      const current=values();
      for(const field of entry().fields||[]) fields.get(field.name).parentElement.hidden=Object.entries(field.when||{}).some(([key,value])=>current[key]!==value);
      drafts[selected]=current;save();
      const args=['start_camera:=false','use_gui:=true','enable_motion:=false'];
      for(const [key,input]of fields)if(!input.parentElement.hidden&&input.value){
        if(key==='enable_motion')args.splice(args.findIndex(arg=>arg.startsWith('enable_motion:=')),1);
        args.push(key+':='+input.value);
      }
      if(isNavigation(selected)){ui.command.textContent=entry().guide;return;}
      ui.command.textContent='104: ros2 launch omnifleet_tutorials vision_'+selected+'.launch.py\n'+args.join(' ')+'\n\n结果图：'+entry().imageTopic+'\n数据：'+entry().ui.dataTopics.map(([topic])=>topic).join('\n');
    }
    function select(id, sync=true) {
      if(id!==selected)previewPending=trackingCases.has(id)||isNavigation(id);
      selected=id;
      ui.followControls.hidden=!['04_08_gesture_person_follow','04_09_body_tracking'].includes(selected);
      ui.bodyMotionControls.hidden=selected!=='04_09_body_tracking';
      ui.distanceControls.hidden=selected!=='04_09_body_tracking';
      ui.tuningControls.hidden=selected!=='04_09_body_tracking';
      ui.clearMap.parentElement.hidden=selected==='04_09_body_tracking';
      if(selected==='04_09_body_tracking'){
        ui.followMode.textContent='Body Tracking C++ · 人体＋深度';
        ui.targetId.hidden=true;ui.lockTarget.disabled=false;
        ui.lockTarget.textContent='开始 / 重新演示';ui.pauseFollow.textContent='停止此案例';
      }else {
        ui.pauseFollow.textContent='暂停跟随';
        if(selected==='04_08_gesture_person_follow'){
          officialTros=true;ui.targetId.hidden=true;ui.lockTarget.disabled=false;
          ui.lockTarget.textContent='开始 / 恢复官方跟随';
        }
      }
      const profile=entry().ui;
      if(sync||!profile.views.includes(selectedView))selectedView=profile.defaultView;
      if(sync||!profile.dataTopics.some(([topic])=>topic===dataTopic))dataTopic=profile.dataTopic;
      ui.view.replaceChildren();
      for(const value of profile.views){const option=document.createElement('option');option.value=value;option.textContent=value==='result'&&selected==='02_07_kcf'?'目标物跟随窗口 · NanoTrack/KCF':viewLabels[value];ui.view.append(option);}
      ui.view.value=selectedView;
      ui.dataTopic.replaceChildren();
      for(const [value,text]of profile.dataTopics){const option=document.createElement('option');option.value=value;option.textContent=text;ui.dataTopic.append(option);}
      ui.dataTopic.value=dataTopic;
      results.clear();frames=0;frameAt=0;ui.result.textContent='等待本案例结果…';
      ui.resultDetails.open=profile.defaultView!=='result';
      ui.title.textContent=entry().title+' · '+(catalog.findIndex(item=>item.id===selected)+1)+'/'+catalog.length;
      ui.focus.textContent='演示重点：'+profile.focus;
      ui.guide.textContent=entry().guide;
      ui.fields.replaceChildren();ui.followRunMode.replaceChildren();fields.clear();
      for(const field of entry().fields||[]) {
        const label=document.createElement('label');label.textContent=field.label;
        const input=document.createElement(field.type==='select'?'select':'input');
        if(field.type==='select')for(const [value,text]of field.options){const option=document.createElement('option');option.value=value;option.textContent=text;input.append(option);}
        else input.type=field.type==='number'?'number':'text';
        input.value=drafts[selected]?.[field.name]??field.default??'';
        input.setAttribute('aria-label',field.label);input.dataset.field=field.name;
        input.onchange=showFields;label.append(input);
        (selected==='04_09_body_tracking'&&field.name==='enable_motion'?ui.followRunMode:ui.fields).append(label);fields.set(field.name,input);
      }
      showFields();renderList();subscribe();if(sync)syncView();render();
    }
    function renderList() {
      const query=ui.search.value.toLowerCase(),group=ui.group.value;
      const key=JSON.stringify([query,group,ui.allCases.open,selected,state?.running]);
      if(key===listKey)return;listKey=key;
      ui.list.replaceChildren();
      for(const item of visibleCases()) {
        if(ui.allCases.open&&((group&&caseGroup(item)!==group)||(query&&!(item.title+' '+item.id).toLowerCase().includes(query))))continue;
        const option=document.createElement('option');option.value=item.id;
        const title = item.id==='02_05_qr'?'02.05 二维码跟随':item.id==='02_06_apriltag'?'02.06 AprilTag 跟随':item.title;
        option.textContent=(state?.running?.some(r=>r.case_id===item.id)?'● ':'')+title+(item.offline?' [离线]':'');ui.list.append(option);
      }
      ui.list.value=selected;
    }
    function send(op, preview=false) {
      if(op==='start')for(const field of entry().fields||[])if(field.required&&!fields.get(field.name).parentElement.hidden&&!fields.get(field.name).value.trim()){message('请填写'+field.label);fields.get(field.name).focus();return;}
      previewPending=false;
      const parameters=values();
      if(preview)parameters.enable_motion='true';
      const request={id:root.crypto?.randomUUID?.()||String(Date.now()),op,case_id:selected,parameters};
      // The installed CDR writer counts string characters as bytes: keep wire JSON ASCII.
      const data=JSON.stringify(request).replace(/[\u007f-\uffff]/g,c=>'\\u'+c.charCodeAt(0).toString(16).padStart(4,'0'));
      try {context.publish(CONTROL,{data});message(op==='restart_slam'?'已请求重启 SLAM 并重新建图':op==='navigation'?'已请求启动 104 导航':op==='start'?'已向104提交开始演示':'已向104提交停止当前案例');}
      catch(error){message('发送失败：'+error.message);}
    }
    function render() {
      if(disposed)return;
      const connected=state&&Date.now()-received<4000;
      if(previewPending&&connected&&!state.busy){
        previewPending=false;
        if(isNavigation(selected)){if(state.phase!=='NAVIGATION')send('navigation');}
        else if(state.phase!=='RUNNING'||state.case_id!==selected||state.motion_enabled!==true)send('start',true);
      }
      ui.restartSlam.disabled=Boolean(state?.busy);
      ui.reconnect.hidden=Boolean(connected);
      ui.running.textContent=connected?(phases[state.phase]||state.phase)+' · '+(catalog.find(item=>item.id===state.case_id)?.title||'没有运行中的案例'):'等待104演示管理器状态';
      const navigation=isNavigation(selected);
      if(navigation&&route?.execution){
        const execution=route.execution;
        const labels={idle:'等待航点',preplanning:'规划中',tracking:'导航中',recovering:'脱困中',canceling:'正在停止',cancel_unconfirmed:'等待停车确认',stopping:'到点停车中',waiting:'停靠等待',completed:'任务完成',failed:'任务失败',canceled:'已停止'};
        ui.running.textContent=entry().title+' · '+(labels[execution.phase]||execution.phase||'等待状态');
        ui.message.textContent=!route.navigation_active&&route.waypoints?.length===0&&execution.phase==='idle'?'航点列表为空':execution.message||'';
        ui.motion.textContent=(execution.waypoint_states||[]).map((value,index)=>
          '航点'+(index+1)+' '+(execution.phase==='failed'&&['正在导航','正在通过','停靠对齐中'].includes(value)?'未完成':value)).join(' · ');
      }
      ui.clearWaypoints.hidden=!navigation;
      ui.clearWaypoints.disabled=Boolean(route?.navigation_active);
      ui.clearWaypoints.title=route?.navigation_active?'请先停止导航，再清除航点':'';
      ui.start.hidden=selected===SINGLE_NAV;
      ui.start.textContent=selected===SINGLE_NAV?'导航到最新航点':navigation?'开始整条路线':'开始 / 重新演示';
      ui.stop.textContent=navigation?'停止导航':'停止当前';
      ui.start.disabled=navigation?Boolean(state?.busy||!route?.nav2_ready||route.navigation_active||!route.waypoints?.length):Boolean(state?.busy);
      const result=results.get(dataTopic);
      const gemini=quality?.camera_backend==='orbbec'||geminiSeen;
      ui.hikCamera.hidden=gemini;ui.geminiCamera.hidden=!gemini;
      if(gemini&&!rgbReadAttempted&&context.callService){rgbReadAttempted=true;void ui.rgbRead.onclick();}
      ui.frames.textContent=navigation?(!route?'等待航点和定位状态':('已录入 '+(route.waypoints?.length||0)+' 个航点 · '+(route.navigation_active?'正在导航':route.nav2_ready?'导航已就绪':'等待定位和导航就绪'))):(frames?'结果图 '+frames+' 帧 · '+Math.max(0,Math.floor((Date.now()-frameAt)/1000))+' 秒前更新':'等待案例结果图')+'；'+(result?'功能数据 '+Math.max(0,Math.floor((Date.now()-result.at)/1000))+' 秒前更新':'等待功能数据');
      ui.quality.hidden=!entry().ui.usesDepth;
      ui.quality.textContent=entry().ui.usesDepth&&quality?'深度有效 '+(quality.source_valid_fraction*100).toFixed(1)+'% · 视觉点云已停用':'';
      if(cameraState){
        const depthText=cameraState.depth_auto_exposure?'自动（上限'+cameraState.depth_auto_exposure_max_us+'μs）':'手动 '+cameraState.depth_exposure_time_us+'μs';
        ui.cameraState.textContent='RGB '+(cameraState.rgb_auto_exposure?'自动曝光':'手动曝光')+' · 深度 '+depthText+' · 设备 '+cameraState.acquisition_frame_rate+'FPS · 原生平滑 '+(cameraState.RangeFilterEnable?'开':'关')+' / 补洞 '+(cameraState.GapFillEnable?'开':'关');
        if(!exposureEdited){ui.exposure.value=cameraState.depth_auto_exposure?cameraState.depth_auto_exposure_max_us:cameraState.depth_exposure_time_us;ui.exposureNumber.value=ui.exposure.value;ui.exposureMode.value=cameraState.depth_exposure_mode||'SingleMode';}
        ui.exposure.min=cameraState.depth_exposure_min_us;ui.exposure.max=cameraState.depth_exposure_max_us;
        ui.exposureNumber.min=cameraState.depth_exposure_min_us;ui.exposureNumber.max=cameraState.depth_exposure_max_us;
        ui.exposureRange.textContent='设备范围：'+cameraState.depth_exposure_min_us+'–'+cameraState.depth_exposure_max_us+' μs；松开滑块立即应用。';
        ui.exposureLabel.textContent=ui.exposureMode.value==='DynamicMode'?'自动曝光上限（μs）':'固定曝光值（μs）';
      }
      ui.exposureValue.textContent=ui.exposure.value+' μs';
    }
    function showResult(){ui.result.textContent=results.get(dataTopic)?.text||'等待本案例结果…';}
    ui.restartSlam.onclick=()=>{send('restart_slam');ui.restartSlamReply.textContent='已请求停止导航并重建地图，等待104状态…';};
    ui.list.onchange=()=>select(ui.list.value);
    ui.reconnect.onclick=()=>{
      const api=root.foxgloveDemoControl;
      if(api?.connect){api.connect('ws://192.168.3.104:8765');message('已重新连接104数据，等待案例状态和实时图像…');}
      else message('当前客户端不支持快捷重连，请重新打开104数据连接。');
    };
    ui.view.onchange=()=>{selectedView=ui.view.value;save();subscribe();syncView();};
    function renderBodyMotion(){
      ui.bodyMotion.disabled=typeof bodyMotion!=='boolean'||bodyMotionBusy||bodyPendingMotion!==undefined;
      ui.bodyMotion.textContent=typeof bodyMotion!=='boolean'?'等待底盘跟随状态':bodyMotion?'关闭底盘跟随':'开启底盘跟随';
    }
    ui.bodyMotion.onclick=async()=>{
      if(typeof bodyMotion!=='boolean'||bodyMotionBusy||bodyPendingMotion!==undefined)return;
      const value=!bodyMotion;bodyMotionBusy=true;renderBodyMotion();
      ui.bodyMotionReply.textContent='正在修改底盘跟随…';
      try{
        const reply=await context.callService('/body_tracking_104/horizon_tracking_RobotCmdVel/set_parameters',{parameters:[{name:'enable_motion',value:{type:1,bool_value:value,integer_value:0,double_value:0,string_value:'',byte_array_value:[],bool_array_value:[],integer_array_value:[],double_array_value:[],string_array_value:[]}}]});
        if(!reply.results?.length||reply.results.some(result=>!result.successful))throw Error(reply.results?.map(result=>result.reason).filter(Boolean).join('; ')||'控制器未接受运动开关');
        bodyPendingMotion=value;ui.bodyMotionReply.textContent='参数已接受，等待C++控制器状态确认…';
      }catch(error){ui.bodyMotionReply.textContent='修改失败：'+error.message;}
      finally{bodyMotionBusy=false;renderBodyMotion();}
    };
    async function applyTuning(names){
      const values=names.map(name=>[name,Number(ui['tuningNumber_'+name].value)]);
      for(const [name,value] of values){const input=ui['tuningNumber_'+name];if(!input.value||!input.validity.valid||!Number.isFinite(value)){ui.tuningReply.textContent='请输入有效参数值';return;}}
      for(const [name,value] of values)tuningState[name].pending=value;
      ui.tuningReply.textContent='已提交，等待C++实际读回…';
      try{
        const parameters=values.map(([name,value])=>({name,value:{type:3,bool_value:false,integer_value:0,double_value:value,string_value:'',byte_array_value:[],bool_array_value:[],integer_array_value:[],double_array_value:[],string_array_value:[]}}));
        const reply=await context.callService('/body_tracking_104/horizon_tracking_RobotCmdVel/set_parameters',{parameters});
        if(!reply.results?.length||reply.results.some(result=>!result.successful))throw Error(reply.results?.map(result=>result.reason).filter(Boolean).join('; ')||'控制器未接受参数');
      }catch(error){for(const [name]of values)tuningState[name].pending=undefined;ui.tuningReply.textContent='修改失败：'+error.message;}
    }
    for(const [name,label,value,min,max]of tuningSpecs){
      const slider=ui['tuning_'+name],input=ui['tuningNumber_'+name];
      slider.oninput=()=>{tuningState[name].edited=true;input.value=slider.value;};
      slider.onchange=()=>applyTuning([name]);
      input.oninput=()=>{tuningState[name].edited=true;if(input.value&&input.validity.valid){slider.max=Math.max(max,Number(input.value));slider.value=input.value;}};
      input.onkeydown=event=>{if(event.key==='Enter'){event.preventDefault();applyTuning([name]);}};
    }
    ui.applyTuning.onclick=()=>applyTuning(tuningSpecs.map(([name])=>name));
    const distanceInputs=value=>{ui.followDistance.max=Math.max(3,value);ui.followDistance.value=ui.followDistanceNumber.value=value;};
    if(Number.isFinite(Number(lastFollowDistance))&&Number(lastFollowDistance)>.1)distanceInputs(Number(lastFollowDistance));
    ui.followDistance.oninput=()=>{distanceEdited=true;ui.followDistanceNumber.value=ui.followDistance.value;};
    ui.followDistanceNumber.oninput=()=>{distanceEdited=true;if(ui.followDistanceNumber.value&&ui.followDistanceNumber.validity.valid){ui.followDistance.max=Math.max(3,Number(ui.followDistanceNumber.value));ui.followDistance.value=ui.followDistanceNumber.value;}};
    ui.applyDistance.onclick=async()=>{
      const value=Number(ui.followDistanceNumber.value);
      if(!ui.followDistanceNumber.value||!ui.followDistanceNumber.validity.valid||!Number.isFinite(value)){ui.distanceReply.textContent='请输入有效的距离（米）';return;}
      pendingDistance=value;ui.distanceReply.textContent='已提交，等待C++控制器读回…';
      try{
        const reply=await context.callService('/body_tracking_104/horizon_tracking_RobotCmdVel/set_parameters',{parameters:[{name:'follow_distance',value:{type:3,bool_value:false,integer_value:0,double_value:value,string_value:'',byte_array_value:[],bool_array_value:[],integer_array_value:[],double_array_value:[],string_array_value:[]}}]});
        if(!reply.results?.length||reply.results.some(result=>!result.successful))throw Error(reply.results?.map(result=>result.reason).filter(Boolean).join('; ')||'控制器未接受距离参数');
      }catch(error){pendingDistance=undefined;ui.distanceReply.textContent='修改失败：'+error.message;}
    };
    ui.followDistance.onchange=()=>ui.applyDistance.click();
    ui.followDistanceNumber.onkeydown=event=>{if(event.key==='Enter'){event.preventDefault();ui.applyDistance.click();}};
    async function rgbService(name,request){
      try{return await context.callService(name,request);}catch(error){
        if(!/timeout|timed out/i.test(error.message))throw error;
        ui.rgbReply.textContent='服务连接超时，正在重试一次…';
        return context.callService(name,request);
      }
    }
    ui.rgbRead.onclick=async()=>{try{const reply=await rgbService('/camera/get_color_exposure',{});if(!reply.success)throw Error(reply.message);const ms=Number(reply.data)/10;ui.rgbExposure.value=ui.rgbExposureNumber.value=ms;ui.rgbActual.textContent=ms.toFixed(1)+' ms（设备读回）';ui.rgbReply.textContent='当前RGB曝光：'+ms.toFixed(1)+' ms';return ms;}catch(error){ui.rgbReply.textContent='读取失败：'+error.message;}};
    ui.rgbApply.onclick=async()=>{
      const mode=ui.rgbMode.value;
      if(mode==='keep'){await ui.rgbRead.onclick();return;}
      const ms=Number(ui.rgbExposureNumber.value);
      if(mode==='manual'&&(!ui.rgbExposureNumber.value||!Number.isFinite(ms)||!ui.rgbExposureNumber.validity.valid)){ui.rgbReply.textContent='请输入0.1–500ms范围内的有效曝光值';return;}
      ui.rgbApply.disabled=true;ui.rgbReply.textContent='正在设置RGB曝光…';
      try{let reply=await rgbService('/camera/set_color_auto_exposure',{data:mode==='auto'});if(!reply.success)throw Error(reply.message);if(mode==='manual'){reply=await rgbService('/camera/set_color_exposure',{data:Math.round(ms*10)});if(!reply.success)throw Error(reply.message);}const actual=await ui.rgbRead.onclick();if(actual!=null)ui.rgbReply.textContent=(mode==='auto'?'相机已开启自动曝光':'手动曝光已生效')+'；当前曝光：'+actual.toFixed(1)+' ms';}
      catch(error){ui.rgbReply.textContent='设置失败：'+error.message;}finally{ui.rgbApply.disabled=false;}
    };
    ui.rgbMode.onchange=()=>{const automatic=ui.rgbMode.value==='auto';ui.rgbExposure.disabled=ui.rgbExposureNumber.disabled=automatic;if(ui.rgbMode.value!=='keep')ui.rgbApply.click();};
    ui.rgbExposure.oninput=()=>{ui.rgbMode.value='manual';ui.rgbExposureNumber.value=ui.rgbExposure.value;};
    ui.rgbExposure.onchange=()=>ui.rgbApply.click();
    ui.rgbExposureNumber.oninput=()=>{ui.rgbMode.value='manual';if(ui.rgbExposureNumber.value&&ui.rgbExposureNumber.validity.valid)ui.rgbExposure.value=ui.rgbExposureNumber.value;};
    ui.rgbExposureNumber.onkeydown=event=>{if(event.key==='Enter'){event.preventDefault();ui.rgbMode.value='manual';ui.rgbApply.click();}};
    ui.geminiExposure.oninput=()=>ui.geminiExposureNumber.value=ui.geminiExposure.value;
    ui.geminiExposureNumber.oninput=()=>{if(ui.geminiExposureNumber.validity.valid)ui.geminiExposure.value=ui.geminiExposureNumber.value;};
    ui.geminiRead.onclick=async()=>{try{const reply=await context.callService('/camera/get_depth_exposure',{});if(!reply.success)throw Error(reply.message);ui.geminiExposure.value=ui.geminiExposureNumber.value=reply.data;ui.geminiReply.textContent='设备读回：'+reply.data;}catch(error){ui.geminiReply.textContent='读取失败：'+error.message;}};
    ui.geminiApply.onclick=async()=>{try{if(!ui.geminiExposureNumber.value||!ui.geminiExposureNumber.validity.valid)throw Error('请输入0–10000范围内整数');const reply=await context.callService('/camera/set_depth_exposure',{data:Number(ui.geminiExposureNumber.value)});if(!reply.success)throw Error(reply.message);await ui.geminiRead.onclick();}catch(error){ui.geminiReply.textContent='设置失败：'+error.message;}};
    ui.geminiExposure.onchange=()=>ui.geminiApply.click();
    ui.geminiExposureNumber.onkeydown=event=>{if(event.key==='Enter'){event.preventDefault();ui.geminiApply.click();}};
    ui.exposure.oninput=()=>{exposureEdited=true;ui.exposureNumber.value=ui.exposure.value;ui.exposureValue.textContent=ui.exposure.value+' μs';};
    ui.exposure.onchange=()=>ui.applyExposure.click();
    ui.exposureNumber.oninput=()=>{exposureEdited=true;if(ui.exposureNumber.value&&ui.exposureNumber.validity.valid){ui.exposure.value=ui.exposureNumber.value;ui.exposureValue.textContent=ui.exposureNumber.value+' μs';}};
    ui.exposureNumber.onkeydown=event=>{if(event.key==='Enter'){event.preventDefault();ui.applyExposure.click();}};
    ui.exposureMode.onchange=()=>{exposureEdited=true;ui.exposure.value=500;ui.exposureNumber.value=500;render();};
    ui.applyExposure.onclick=()=>{
      const value=Number(ui.exposureNumber.value);
      if(!Number.isFinite(value)||!ui.exposureNumber.value||!ui.exposureNumber.validity.valid){ui.cameraReply.textContent='请输入设备范围内的有效深度曝光值';return;}
      cameraRequest=root.crypto?.randomUUID?.()||String(Date.now());
      const mode=ui.exposureMode.value,key=mode==='DynamicMode'?'depth_auto_exposure_max_us':'depth_exposure_time_us';
      try{context.publish(CAMERA_CONTROL,{data:JSON.stringify({id:cameraRequest,depth_exposure_mode:mode,[key]:value,persist:ui.saveExposure.checked})});ui.cameraReply.textContent='已提交，等待设备读回…';}
      catch(error){ui.cameraReply.textContent='发送失败：'+error.message;}
    };
    ui.dataTopic.onchange=()=>{dataTopic=ui.dataTopic.value;showResult();save();if(selectedView==='data')syncView();};
    ui.allCases.ontoggle=ui.group.onchange=ui.search.oninput=renderList;
    for(const [name,step]of [['previous',-1],['next',1]])ui[name].onclick=()=>{const items=visibleCases();const index=items.findIndex(item=>item.id===selected);select(items[Math.max(0,Math.min(items.length-1,index+step))].id);};
    function routeCommand(op){
      try{
        if(op==='start'&&selected===SINGLE_NAV){
          context.publish(WAYPOINTS+'/navigate_to',{data:JSON.stringify({index:route.waypoints.length})});
          message('已发送单点导航请求');
        }else{context.publish(WAYPOINTS+'/'+op,{});message(op==='clear'?'已发送清除航点请求':op==='start'?'已发送路线启动请求':'已发送导航停止请求');}
      }
      catch(error){message('航点请求失败：'+error.message);}
    }
    ui.start.onclick=()=>isNavigation(selected)?routeCommand('start'):send('start');
    ui.stop.onclick=()=>isNavigation(selected)?routeCommand('stop'):send('stop');
    ui.clearWaypoints.onclick=()=>routeCommand('clear');
    for(const op of ['start','stop','clear'])context.advertise?.(WAYPOINTS+'/'+op,'std_msgs/msg/Empty');
    context.advertise?.(WAYPOINTS+'/navigate_to','std_msgs/msg/String',{datatypes:new Map([['std_msgs/msg/String',{definitions:[{name:'data',type:'string',isArray:false,isComplex:false}]}]])});
    function followCommand(request){try{context.publish(FOLLOW_CONTROL,{data:JSON.stringify(request)});message('已向104提交跟随操作');}catch(error){message('发送失败：'+error.message);}}
    ui.lockTarget.onclick=()=>{if(selected==='04_09_body_tracking')send('start');else if(officialTros)followCommand({op:'resume'});else if(ui.targetId.value)followCommand({op:'lock',track_id:Number(ui.targetId.value)});};
    ui.pauseFollow.onclick=()=>selected==='04_09_body_tracking'?send('stop'):followCommand({op:'pause'});
    ui.clearMap.onclick=async()=>{
      ui.clearMap.disabled=true;ui.mapReply.textContent='正在清空当前地图…';
      try{
        context.publish(FOLLOW_CONTROL,{data:JSON.stringify({op:'pause'})});
        const reply=await context.callService('/mola_realtime_nav_grid/clear',{});
        if(reply?.success!==true)throw Error(reply?.message||'栅格清空未确认');
        const results=await Promise.allSettled(['/global_costmap/clear_entirely_global_costmap','/local_costmap/clear_entirely_local_costmap'].map(service=>context.callService(service,{})));
        const errors=results.filter(result=>result.status==='rejected');
        ui.mapReply.textContent=reply.message+(errors.length?'；代价地图刷新未全部确认':'；全局/局部代价缓存已清空');
      }catch(error){ui.mapReply.textContent='清空失败：'+error.message;}
      finally{ui.clearMap.disabled=false;}
    };
    ui.fields.onsubmit=event=>{event.preventDefault();send('start');};
    context.advertise?.(CONTROL,'std_msgs/msg/String',{datatypes:new Map([['std_msgs/msg/String',{definitions:[{name:'data',type:'string',isArray:false,isComplex:false}]}]])});
    context.advertise?.(CAMERA_CONTROL,'std_msgs/msg/String',{datatypes:new Map([['std_msgs/msg/String',{definitions:[{name:'data',type:'string',isArray:false,isComplex:false}]}]])});
    context.advertise?.(FOLLOW_CONTROL,'std_msgs/msg/String',{datatypes:new Map([['std_msgs/msg/String',{definitions:[{name:'data',type:'string',isArray:false,isComplex:false}]}]])});
    context.watch('currentFrame');
    context.onRender=(renderState,done)=>{
      try {
        // A desktop shortcut can replace the layout while this control stays
        // mounted. Reconcile that saved selection with the visible controls.
        const config=root.foxgloveDemoControl?.layout?.()?.data?.configById?.[PANEL];
        if(config&&catalog.some(item=>item.id===config.selectedCase)&&config.selectedCase!==selected){
          selectedView=config.selectedView;dataTopic=config.dataTopic;Object.assign(views,config.views);
          drafts=config.parametersByCase||drafts;select(config.selectedCase,false);
        }else if(config?.selectedView&&entry().ui.views.includes(config.selectedView)&&config.selectedView!==selectedView){
          selectedView=config.selectedView;ui.view.value=selectedView;subscribe();
        }
        if(config?.dataTopic&&entry().ui.dataTopics.some(([topic])=>topic===config.dataTopic)&&config.dataTopic!==dataTopic){
          dataTopic=config.dataTopic;ui.dataTopic.value=dataTopic;showResult();
        }
        for(const event of renderState.currentFrame||[]) {
          if(event.topic===RGB)updateRgb(event.message);
          else if(event.topic===WAYPOINTS+'/catalog')route=JSON.parse(event.message.data);
          else if(event.topic===WAYPOINTS+'/status')message(event.message.data);
          else if(event.topic===STATUS) {
            state=JSON.parse(event.message.data);received=Date.now();message(state.message==='案例进程已启动，等待结果话题'||state.phase==='RUNNING'&&state.message==='当前视觉案例已停止'?'案例进程运行中':state.message);
            if(selected==='04_09_body_tracking'&&bodyMotion===undefined&&state.case_id===selected&&state.phase==='RUNNING'&&typeof state.motion_enabled==='boolean'&&motionRequestId!==state.request_id){
              motionRequestId=state.request_id;fields.get('enable_motion').value=String(state.motion_enabled);showFields();
            }
            if(!state.running?.length)ui.motion.textContent='当前没有运行中的案例';
            const text=state.logs.join('\n');
            if(text!==lastLogs){const bottom=ui.logs.scrollHeight-ui.logs.scrollTop-ui.logs.clientHeight<40;lastLogs=text;ui.logs.textContent=text||'当前案例可能来自旧SSH终端；新启动案例的日志会进入此面板。';if(bottom)ui.logs.scrollTop=ui.logs.scrollHeight;}
            renderList();
          } else if(event.topic===CAMERA_STATUS){
            cameraState=JSON.parse(event.message.data);
            const reply=cameraState.last_control;
            if(reply && cameraRequest && reply.id===cameraRequest){
              const valueText=reply.depth_auto_exposure?'自动，上限'+reply.depth_auto_exposure_max_us+'μs':reply.depth_exposure_time_us+'μs';
              ui.cameraReply.textContent=reply.success?'已生效：'+valueText+' / '+reply.acquisition_frame_rate+'FPS'+(reply.persisted?'，已永久保存':'，本次运行有效'):'修改失败：'+reply.error;
              if(reply.success)exposureEdited=false;
            }
          } else if(event.topic==='/camera/rgbd/visualization_status')quality=JSON.parse(event.message.data);
          else if(event.topic===(entry().displayTopic||entry().imageTopic)){frames++;frameAt=Date.now();}
          else if(entry().ui.dataTopics.some(([topic])=>topic===event.topic)) {
            let value=event.message.data??event.message;
            if(typeof value==='string'){try{value=JSON.parse(value);}catch{}}
            if(typeof value?.motion_enabled==='boolean')ui.motion.textContent=value.motion_enabled?'实机跟随 · enable_motion=true':'识别演示 · enable_motion=false';
            if(typeof value?.enable_motion==='boolean')ui.motion.textContent=value.enable_motion?'实机跟随 · enable_motion=true':'识别演示 · enable_motion=false';
            if(event.topic==='/vision/gesture_follow/status'&&Array.isArray(value?.tracks)){
              officialTros=value.controller_backend==='tros_person_following_cpp';
              ui.followMode.textContent=value.auto_follow?'人体自动跟随 · 手势已停用':'人体跟随 · 人物选择';
              ui.guide.textContent=value.auto_follow?'最终综合案例。当前自动锁定模式：识别到人即锁定ID，先居中再通过Nav2跟随，保持约'+Number(value.follow_distance_m??1).toFixed(2)+'米，太近则后退。无有效深度时先居中，再朝人物分段靠近取深度。多人时先选画面最居中的人。暂停后可用上方选人按钮恢复。':entry().guide;
              const key=JSON.stringify(value.tracks.map(track=>track.id));
              if(key!==targetListKey){const previous=ui.targetId.value;targetListKey=key;ui.targetId.replaceChildren();for(const track of value.tracks){const option=document.createElement('option');option.value=String(track.id);option.textContent='人物 ID '+track.id;ui.targetId.append(option);}if(value.tracks.some(track=>String(track.id)===previous))ui.targetId.value=previous;}
              ui.targetId.hidden=officialTros;
              ui.lockTarget.textContent=officialTros?'开始 / 恢复官方跟随':'锁定并跟随所选人物';
              ui.lockTarget.disabled=!officialTros&&!value.tracks.length;
              if(officialTros){
                ui.followMode.textContent='官方 TROS C++ 人体跟随 · 手势已停用';
                ui.guide.textContent='方案A。104 YOLO分割/跟踪与真实RGB-D测距 → 官方TROS C++状态机 → 现有MOLA/Nav2。按原版策略选人、滞回、限频更新目标并主动寻找丢失目标。跟随距离带约1米；过近停车，不主动后退。暂停后点击开始/恢复。';
              }
              const modes={HOLD:'保持距离',FOLLOW:'跟随',BACKOFF:'后退拉开距离',APPROACH_FOR_DEPTH:'接近获取深度',VISIBLE_NO_DEPTH:'尚无有效深度'};
              const mode=officialTros?value.follow_control_state:value.state==='IDLE'?(value.auto_follow?'等待人物，出现即锁定':'等待锁定'):value.state==='PAUSED'?'已暂停':value.centering?'居中转向':modes[value.follow_control_state]||value.state;
              const goal=value.nav_goal;
              ui.followState.textContent=(value.operator_message||'')+' · '+mode+(value.person_range_m==null?'':' · '+value.person_range_m.toFixed(2)+'m')+(goal?' · 目标 map ('+goal.x.toFixed(2)+', '+goal.y.toFixed(2)+')':' · 当前无移动目标');
            }
            if(event.topic==='/vision/body_tracking/status'&&value?.controller_backend==='body_tracking_cpp'){
              if(typeof value.body_tracking?.motion_enabled==='boolean'){
                const previousMotion=bodyMotion;
                bodyMotion=value.body_tracking.motion_enabled;
                if(bodyPendingMotion===bodyMotion){bodyPendingMotion=undefined;ui.bodyMotionReply.textContent=bodyMotion?'已开启底盘跟随（C++控制器读回）；ID为空时需OK或数字手势锁定':'已关闭底盘跟随（C++控制器读回），人物识别和跟踪保留';}
                if(previousMotion!==bodyMotion&&fields.get('enable_motion')?.value!==String(bodyMotion)){fields.get('enable_motion').value=String(bodyMotion);showFields();}
                renderBodyMotion();
              }
              geminiSeen=value.camera_backend==='orbbec';
              const velocity=value.velocity_request||{};
              const digits=Boolean(value.gesture_controls?.one);
              ui.followMode.textContent=value.gestures_enabled?(digits?'手势控制 · 1进 2退 · 3顺一圈 4逆一圈':'Body Tracking C++ · OK / 张掌＋深度'):'Body Tracking C++ · 人体＋深度';
              if(value.gesture_controls)ui.guide.textContent=digits?'1食指前进；2食中指后退；3三指顺时针转一圈后停车；4收起拇指、其余四指伸出，逆时针转一圈后停车；五指张掌停止并解除锁定。1/2保持到张掌或切换手势；3/4按里程计累计360°，保持同一手势不会重复转，变换手势后再摆可重新转。OK切回按目标距离跟随。':'OK手势锁定本人并开始跟随；张掌停止并解除锁定，需要再次做OK才能重新跟随。手势与人物ID绑定，保留深度控距、转向和过近后退。';
              const modes={ROTATION_DONE:'已转一圈，已停车',WAIT_ODOM:'等待读取转角',GESTURE_FORWARD:'数字1 · 前进',GESTURE_BACKWARD:'数字2 · 后退',GESTURE_SPIN_CW:'数字3 · 顺时针转一圈',GESTURE_SPIN_CCW:'数字4 · 逆时针转一圈',WAIT_PERSON:'人物暂时丢失，已停车',BACKOFF:'后退拉开距离',HOLD:'保持距离',WAIT_DEPTH:'等待有效深度',FOLLOW:'前进跟随',CENTER:'转向对准人物',APPROACH_FOR_DEPTH:'靠近获取深度',INITING:value.gestures_enabled?(digits?'等待OK或数字手势':'等待OK手势锁定'):'等待人体',ORIGINAL:'跟随'};
              const tuning=value.body_tracking?.tuning;
              if(tuning){
                let acknowledged=false;
                for(const [name,label,initial,min,max,step,unit]of tuningSpecs){
                  const actual=Number(tuning[name]);if(!Number.isFinite(actual))continue;
                  const state=tuningState[name];ui['tuningActual_'+name].textContent=actual.toFixed(2)+unit;
                  if(state.pending!=null&&Math.abs(state.pending-actual)<1e-6){state.pending=undefined;state.edited=false;acknowledged=true;}
                  if(!state.edited){ui['tuning_'+name].max=Math.max(max,actual);ui['tuning_'+name].value=ui['tuningNumber_'+name].value=actual;}
                }
                if(acknowledged)ui.tuningReply.textContent=Object.values(tuningState).some(state=>state.pending!=null)?'等待其余参数读回…':'已生效，控制器读回确认';
              }
              const range=value.person_range_m;
              const target=Number(value.body_tracking?.target_distance_m??value.follow_distance_m??lastFollowDistance??1);
              if(Number.isFinite(target)&&(value.body_tracking?.target_distance_m!=null||value.follow_distance_m!=null)&&lastFollowDistance!==target){lastFollowDistance=target;save();}
              ui.actualDistance.textContent=target.toFixed(2)+' m（控制器读回）';
              if(!distanceEdited)distanceInputs(target);
              if(pendingDistance!=null&&Math.abs(pendingDistance-target)<.001){distanceEdited=false;pendingDistance=undefined;distanceInputs(target);ui.distanceReply.textContent='已生效并保存：'+target.toFixed(2)+' m';}
              ui.followState.textContent=(modes[value.follow_control_state]||value.state)+' · ID '+(value.track_id??'无')+
                (value.gestures_enabled?' · 手势 '+({okay:'OK',one:'1',victory:'2',three:'3',four:'4',open_palm:'五指张掌',unknown:'未识别'}[value.gesture]||value.gesture||'未识别')+(value.gesture_owner==null?'':' / 人物 '+value.gesture_owner):'')+
                ' · v='+Number(velocity.linear_x||0).toFixed(2)+'m/s，ω='+Number(velocity.angular_z||0).toFixed(2)+'rad/s'+
                (range==null?' · 当前无有效底盘测距':' · 底盘到人物 '+range.toFixed(2)+'m')+
                (value.body_tracking?.gesture_motion?.startsWith('GESTURE_SPIN')?' · 已转 '+Math.max(0,Number(value.body_tracking.rotation_degrees||0)).toFixed(1)+'° / 360°；'+(value.body_tracking.rotation_done?'完成停车，变换手势再摆可重转':'五指张掌可中止')+'；不经Nav2':value.body_tracking?.gesture_motion&&value.body_tracking.gesture_motion!=='NONE'?' · 数字动作已保持，五指张掌停止；距离仅显示；不经Nav2':' · 目标'+target.toFixed(2)+'m；小于'+(target-.10).toFixed(2)+'m后退，回到目标停；不经Nav2');
            }
            results.set(event.topic,{text:(typeof value==='string'?value:JSON.stringify(value,null,2)).slice(0,6000),at:Date.now()});showResult();
          }
        }
        render();
      } catch(error){message('状态解析失败：'+error.message);}finally{done();}
    };
    const timer=setInterval(render,500);select(selected,false);
    if(isNavigation(selected)||selectedView==='result'&&trackingCases.has(selected)||!root.foxgloveDemoControl?.layout?.()?.data)syncView();
    return ()=>{disposed=true;clearInterval(timer);context.subscribe([]);context.unadvertise?.(CONTROL);context.unadvertise?.(CAMERA_CONTROL);context.unadvertise?.(FOLLOW_CONTROL);for(const op of ['start','stop','clear','navigate_to'])context.unadvertise?.(WAYPOINTS+'/'+op);context.onRender=undefined;el.remove();};
  }

  function initKcfPanel(context) {
    const color=context.initialState?.followKind==='color';
    const marker=context.initialState?.markerKind;
    const caseId=context.initialState?.caseId||(color?(context.initialState?.caseId||'04_01_color_follow'):marker==='qr'?'02_05_qr':marker==='apriltag'?'02_06_apriltag':'02_07_kcf');
    const body=caseId==='04_09_body_tracking';
    const follower=color?(caseId==='02_04_color'?'/course_color_box_follow':'/course_target_follow'):marker?'/'+marker+'_follower':'/kcf_follower';
    const KCF_STATUS=body?'/vision/body_tracking/status':color?'/vision/target_follow/status':marker?'/vision/'+marker+'/follow/status':'/omnifleet_vision/kcf/status';
    const el=document.createElement('div');el.className='vision-demo vision-kcf-window'+(body?' vision-body-preview':'');
    el.innerHTML=`<style>
      .vision-demo{height:100%;box-sizing:border-box;overflow:auto;padding:14px;color:#e5edf7;background:#151b25;font:14px/1.5 "Microsoft YaHei",sans-serif}
      .vision-demo h2{font-size:21px;margin:0 0 4px}.vision-demo p{margin:6px 0}.vision-demo small{color:#a9bbcf}
      .vision-demo input,.vision-demo select,.vision-demo textarea{box-sizing:border-box;width:100%;font:inherit;color:#e8edf6;background:#202a39;border:1px solid #43536b;border-radius:5px;padding:7px;margin:4px 0}
      .vision-demo select[data-ui=list]{padding:3px;min-height:160px}.vision-demo option{padding:6px}.vision-demo option:checked{background:#245583}
      .vision-demo button{font:inherit;border:1px solid #4c6585;border-radius:5px;padding:8px;color:white;background:#293f59;cursor:pointer}
      .vision-demo button:disabled{opacity:.55;cursor:default}.vision-demo .vd-row{display:flex;gap:7px}.vision-demo .vd-row>*{flex:1;min-width:0}
      .vision-demo .vd-card{padding:10px;border:1px solid #34455b;border-radius:7px;margin:10px 0}.vision-demo [data-ui=start]{background:#1467ad}.vision-demo [data-ui=stop]{background:#9a343f}
      .vision-demo [data-ui=message]{white-space:pre-wrap;color:#9fd3ff}.vision-demo pre{white-space:pre-wrap;overflow:auto;max-height:240px;font:12px/1.45 Consolas,monospace;color:#c5d6e9}
      .vision-demo [data-ui=logs]{height:180px;max-height:300px;background:#101620;padding:8px}.vision-demo label{display:block;margin:5px 0}.vision-demo details{margin:8px 0}
    </style><style>
      .vision-kcf-window{overflow:auto;padding:12px}
      .vision-kcf-window [data-ui=kcfControls]{margin:0;padding:0;border:0;display:flex;flex-direction:column;min-height:0}
      .vision-kcf-window [data-ui=kcfPicker]{flex:none;width:min(100%,1120px);aspect-ratio:16/9;min-height:0;align-self:center;background:#0d121a;overflow:hidden}
      .vision-kcf-window [data-ui=kcfPreview],.vision-kcf-window [data-ui=kcfCanvas]{width:100%;height:100%;object-fit:contain}
      .vision-kcf-window [data-ui=kcfLoading]{position:absolute;inset:0;margin:auto;width:32px;height:32px;box-sizing:border-box;border:3px solid #34455b;border-top-color:#74b9ff;border-radius:50%;animation:vision-rgb-spin .8s linear infinite;pointer-events:none}
      .vision-body-preview [data-ui=kcfControls] > :not([data-ui=kcfPicker]):not([data-ui=kcfReply]){display:none}
      .vision-body-preview [data-ui=kcfCanvas]{pointer-events:none}
      @keyframes vision-rgb-spin{to{transform:rotate(360deg)}}
      .vision-kcf-window [data-ui=kcfPreview]:not([hidden]){display:block}
      .vision-kcf-window [data-ui=start]{background:#1467ad}.vision-kcf-window [data-ui=stop]{background:#9a343f}
    </style>    <div class="vd-card" data-ui=kcfControls><strong>${color?'颜色目标跟随':marker?'二维码 / AprilTag 自动识别并跟随':'框选物体并跟随'}</strong><div class="vd-row" style="margin:6px 0"><button data-ui=start>开始 / 重新跟踪</button><button data-ui=stop>停止跟随</button></div>
      <p>${color?'点击颜色检测框后，只检测并跟踪选中的色块。点击“清除跟踪”停车并恢复全部颜色检测，再选择新目标。底盘运动由下方开关控制。':marker?'无需拖框。识别后保留二维码内容或标签ID，解码间隙使用KCF连续跟踪；底盘运动由下方按钮控制。重新开始可重新选择目标。':'点击“开始 / 重新跟踪”，然后在下面实时画面拖框，松手锁定目标。底盘是否运动由下方按钮控制；再次拖框可切换物体，“停止跟随”结束案例。'}</p>
      ${color?`<details ><summary>预设颜色（可选）</summary><label>跟随颜色<select data-ui=selectedColor disabled><option value=red>红色</option><option value=yellow>黄色</option><option value=green>绿色</option><option value=blue>蓝色</option><option value=picked disabled>点击选中的颜色目标</option></select></label><button data-ui=applyColor disabled>应用预设颜色</button></details><button data-ui=clearColor>清除跟踪 · 恢复全部颜色检测</button><p data-ui=colorActual>等待读取检测与跟随颜色</p><p data-ui=colorReply>点击检测框选择目标；选中后需先清除跟踪才能重新选择。</p>`:''}
      ${marker==='apriltag'?'<label>跟随测距来源<select data-ui=rangeSource><option value=depth>配准深度图 · 真实深度采样</option><option value=rgb>纯RGB · 210mm标签位姿估距</option></select></label><p data-ui=rangeSourceReply>RGB识别同一标签，两种距离来源可热切换。</p>':''}
      <div data-ui=kcfPicker style="position:relative;touch-action:none"><span data-ui=kcfLoading role="status" aria-label="正在加载实时图像"></span><canvas data-ui=kcfCanvas style="position:absolute;inset:0;width:100%;height:100%;cursor:crosshair"></canvas></div>
      <p data-ui=kcfReply>${marker||color?'等待自动识别目标':'等待框选；尚未指定目标。'}</p>
      <button data-ui=kcfMotion disabled>等待底盘跟随状态</button><p data-ui=kcfMotionReply>关闭运动仍保留目标框和ID。</p>
      <label>与物体保持距离：<strong data-ui=kcfActualDistance>等待读回</strong>
        <span class="vd-row"><input data-ui=kcfDistance type=range min=0.2 max=3.5 step=0.05 value=2 aria-label="物体跟随距离滑块"><input data-ui=kcfDistanceNumber type=number min=0.2 max=3.5 step=0.05 value=2 aria-label="物体跟随距离米"></span></label>
      <button data-ui=kcfApplyDistance>应用跟随距离</button><p data-ui=kcfDistanceReply></p>
      <small>单位米，范围大于0.2且小于3.5。输入后按回车、点击应用或松开滑块生效，无需重选目标。成功设置后永久保存在104，重启读取本案例上一次的值，各案例独立保存。</small></div>
`;
    context.panelElement.append(el);
    const ui={};el.querySelectorAll('[data-ui]').forEach(item=>{ui[item.dataset.ui]=item;item.dataset.testid='vision-'+item.dataset.ui;});
    let kcfDrag,kcfSourceWidth,kcfDistanceEdited=false,kcfPendingDistance,kcfMotion,kcfPendingMotion,kcfMotionBusy=false,kcfStopReason='';
    let detectorColor,controllerColor,detectorSample,colorBusy=false,pendingColor,pickPendingId,pickTimer,kcfImageStamp=0,overlay,caseReady=false;
    const colorNames={red:'红色',yellow:'黄色',green:'绿色',blue:'蓝色'};
    const colorLabel=value=>colorNames[value]||(typeof value==='string'&&value.startsWith('picked_')?(detectorSample?.name===value&&colorNames[detectorSample.source_color]?colorNames[detectorSample.source_color]+'（已点击）':'画面取色'):value===''?'全部颜色':value==='__click_target__'?'等待点击检测框':'等待读回');
    async function callFollowService(name,request){
      for(let attempt=0;;attempt++)try{return await context.callService(name,request);}
      catch(error){if(attempt>=3||!/not been advertised|not advertised/i.test(error.message))throw error;await new Promise(resolve=>setTimeout(resolve,500));}
    }
    function renderColor(){
      if(!color)return;
      ui.selectedColor.disabled=ui.applyColor.disabled=Boolean(detectorColor)||colorBusy||pendingColor!==undefined||detectorColor===undefined||controllerColor===undefined;
      ui.clearColor.disabled=detectorColor===undefined||controllerColor===undefined;
      ui.colorActual.textContent=detectorColor?'仅检测并跟踪：'+colorLabel(detectorColor):'检测：全部颜色；跟随：'+colorLabel(controllerColor);
      if(detectorSample&&detectorSample.name===detectorColor){
        ui.colorActual.textContent+=' · HSV '+detectorSample.hsv.join('/');
        const bgr=detectorSample.bgr;ui.colorActual.style.borderLeft='8px solid rgb('+[bgr[2],bgr[1],bgr[0]].join(',')+')';ui.colorActual.style.paddingLeft='8px';
      }else ui.colorActual.style.borderLeft='';
      if(pendingColor!==undefined&&detectorColor===pendingColor&&controllerColor===(pendingColor||'__click_target__')){
        ui.colorReply.textContent=pendingColor?'已应用'+colorLabel(pendingColor)+'（检测器与控制器读回）':'已清除跟踪并停车，全部颜色检测已恢复';pendingColor=undefined;
        ui.selectedColor.disabled=ui.applyColor.disabled=colorBusy||Boolean(detectorColor);
      }
      if(!colorBusy&&pendingColor===undefined&&detectorColor===controllerColor)ui.selectedColor.value=String(controllerColor).startsWith('picked_')?'picked':controllerColor;
    }
    if(color){
      ui.applyColor.onclick=async()=>{
        if(detectorColor){ui.colorReply.textContent='已锁定目标，请先清除跟踪';return;}
        const value=ui.selectedColor.value;if(value==='picked'){ui.colorReply.textContent='请直接点击实时画面中的色块取色';return;}
        colorBusy=true;renderColor();ui.colorReply.textContent='正在切换颜色…';
        try{
          for(const [node,name]of [[follower,'class_filter'],['/course_color','selected_color']]){
            const reply=await callFollowService(node+'/set_parameters',{parameters:[{name,value:{type:4,bool_value:false,integer_value:0,double_value:0,string_value:value,byte_array_value:[],bool_array_value:[],integer_array_value:[],double_array_value:[],string_array_value:[]}}]});
            if(!reply.results?.length||reply.results.some(r=>!r.successful))throw Error(reply.results?.map(r=>r.reason).join('; ')||'颜色参数未接受');
          }
          pendingColor=value;ui.colorReply.textContent='已提交，等待两端颜色读回…';
        }catch(error){ui.colorReply.textContent='切换失败：'+error.message;}
        finally{colorBusy=false;renderColor();}
      };
      ui.selectedColor.onchange=()=>ui.applyColor.onclick();
      ui.clearColor.onclick=()=>{
        pickPendingId=root.crypto?.randomUUID?.()||String(Date.now());colorBusy=true;pendingColor=undefined;renderColor();
        try{context.publish(COLOR_PICK,{data:JSON.stringify({id:pickPendingId,op:'clear'})});ui.colorReply.textContent='正在清除跟踪并停车…';}
        catch(error){colorBusy=false;pickPendingId=undefined;renderColor();ui.colorReply.textContent='清除失败：'+error.message;return;}
        clearTimeout(pickTimer);const id=pickPendingId;pickTimer=setTimeout(()=>{if(pickPendingId===id){pickPendingId=undefined;colorBusy=false;renderColor();ui.colorReply.textContent='清除请求未收到104确认，请检查连接';}},5000);
      };
    }
    const stringType={datatypes:new Map([['std_msgs/msg/String',{definitions:[{name:'data',type:'string',isArray:false,isComplex:false}]}]])};
    context.advertise?.(CONTROL,'std_msgs/msg/String',stringType);
    if(color)context.advertise?.(COLOR_PICK,'std_msgs/msg/String',stringType);
    function send(op){
      const config=root.foxgloveDemoControl?.layout?.()?.data?.configById?.[PANEL];
      const parameters=config?.parametersByCase?.[caseId]||{enable_motion:marker||color?'false':'true'};
      try{context.publish(CONTROL,{data:JSON.stringify({id:root.crypto?.randomUUID?.()||String(Date.now()),op,case_id:caseId,parameters})});ui.kcfReply.textContent=op==='start'?'已提交开始跟踪，等待104状态…':'已提交停止跟随…';}
      catch(error){ui.kcfReply.textContent='请求发送失败：'+error.message;}
    }
    ui.start.onclick=()=>send('start');ui.stop.onclick=()=>send('stop');
    function renderMotion(){
      ui.kcfMotion.disabled=typeof kcfMotion!=='boolean'||kcfMotionBusy||kcfPendingMotion!==undefined;
      ui.kcfMotion.textContent=kcfMotion?'关闭底盘跟随':'开启底盘跟随';
    }
    ui.kcfMotion.onclick=async()=>{
      if(typeof kcfMotion!=='boolean'||kcfMotionBusy||kcfPendingMotion!==undefined)return;
      const value=!kcfMotion;kcfMotionBusy=true;renderMotion();ui.kcfMotionReply.textContent='正在修改底盘跟随…';
      try{
        const reply=await callFollowService(follower+'/set_parameters',{parameters:[{name:'enable_motion',value:{type:1,bool_value:value,integer_value:0,double_value:0,string_value:'',byte_array_value:[],bool_array_value:[],integer_array_value:[],double_array_value:[],string_array_value:[]}}]});
        if(!reply.results?.length||reply.results.some(result=>!result.successful))throw Error(reply.results?.map(result=>result.reason).filter(Boolean).join('; ')||'控制器未接受运动参数');
        const api=root.foxgloveDemoControl,current=api?.layout?.();
        if(current?.data&&api?.setLayout){
          const data=JSON.parse(JSON.stringify(current.data));
          const config=data.configById[PANEL];config.parametersByCase??={};config.parametersByCase[caseId]??={};
          config.parametersByCase[caseId].enable_motion=String(value);
          api.setLayout(current.name||'104 视觉功能演示',data);
        }
        kcfPendingMotion=value;
        ui.kcfMotionReply.textContent='参数已接受，等待控制器状态确认…';
      }catch(error){ui.kcfMotionReply.textContent='修改失败：'+error.message;}
      finally{kcfMotionBusy=false;renderMotion();}
    };
    context.advertise?.(KCF_ROI,'sensor_msgs/msg/RegionOfInterest',{datatypes:new Map([
      ['sensor_msgs/msg/RegionOfInterest',{definitions:[
        ...['x_offset','y_offset','height','width'].map(name=>({name,type:'uint32',isArray:false,isComplex:false})),
        {name:'do_rectify',type:'bool',isArray:false,isComplex:false}
      ]}]
    ])});
    function kcfPoint(event){
      const rect=ui.kcfCanvas.getBoundingClientRect();
      const scale=Math.min(rect.width/ui.kcfCanvas.width,rect.height/ui.kcfCanvas.height);
      const left=rect.left+(rect.width-ui.kcfCanvas.width*scale)/2;
      const top=rect.top+(rect.height-ui.kcfCanvas.height*scale)/2;
      return [Math.max(0,Math.min(ui.kcfCanvas.width,(event.clientX-left)/scale)),
              Math.max(0,Math.min(ui.kcfCanvas.height,(event.clientY-top)/scale))];
    }
    function drawKcfBox(end){
      const canvas=ui.kcfCanvas, pen=canvas.getContext('2d');
      pen.clearRect(0,0,canvas.width,canvas.height);pen.strokeStyle='#ffdc00';pen.lineWidth=2;
      pen.strokeRect(kcfDrag[0],kcfDrag[1],end[0]-kcfDrag[0],end[1]-kcfDrag[1]);
    }
    function drawOverlay() {
      if(kcfDrag)return;
      const canvas=ui.kcfCanvas,pen=canvas.getContext('2d');
      pen.clearRect(0,0,canvas.width,canvas.height);
      if(!overlay||!kcfImageStamp||Math.abs(overlay.stamp-kcfImageStamp)>.5)return;
      const sx=canvas.width/(overlay.width||canvas.width),sy=canvas.height/(overlay.height||canvas.height);
      pen.strokeStyle='#74e9a8';pen.fillStyle=pen.strokeStyle;pen.lineWidth=2;pen.font='14px sans-serif';
      for(const track of overlay.tracks){
        if(!Array.isArray(track.bbox)||track.bbox.length!==4||!track.bbox.every(Number.isFinite))continue;
        const [x,y,a,b]=track.bbox;
        pen.strokeRect(x*sx,y*sy,(body?a-x:a)*sx,(body?b-y:b)*sy);
        const id=track.track_id??track.id,depth=track.foreground?.depth_m??overlay.depth;
        const label=[track.color??track.class??(id==null?'':'ID '+id),Number.isFinite(depth)?depth.toFixed(2)+' m':''].filter(Boolean).join(' ');
        if(label)pen.fillText(label,x*sx,Math.max(14,y*sy-4));
      }
    }
    function setOverlay(value,tracks){
      const stamp=value.source_stamp??value.stamp;
      const seconds=Array.isArray(stamp)?Number(stamp[0])+Number(stamp[1])*1e-9:
        typeof stamp==='object'&&stamp?Number(stamp.sec)+Number(stamp.nanosec??stamp.nsec??0)*1e-9:Number(stamp);
      overlay={tracks:tracks||[],stamp:Number.isFinite(seconds)?seconds:kcfImageStamp,
        width:value.rgb_resolution?.[0]??value.image_width,height:value.rgb_resolution?.[1]??value.image_height,depth:value.depth_m};
      drawOverlay();
    }
    function syncRgb() {
      if(sharedRgb.parentNode!==ui.kcfPicker)return;
      if(!sharedRgb.frameStamp||!sharedRgb.naturalWidth)return;
      ui.kcfLoading.hidden=caseReady;
      if(ui.kcfCanvas.width!==sharedRgb.naturalWidth||ui.kcfCanvas.height!==sharedRgb.naturalHeight){
        ui.kcfCanvas.width=sharedRgb.naturalWidth;ui.kcfCanvas.height=sharedRgb.naturalHeight;
      }
      kcfImageStamp=sharedRgb.frameStamp;drawOverlay();
    }
    ui.kcfCanvas.onpointerdown=event=>{
      if(marker||body||!kcfImageStamp)return;
      if(color){
        if(detectorColor){ui.colorReply.textContent='已锁定此色块，请先点击清除跟踪再选择其他目标';return;}
        event.preventDefault();const [x,y]=kcfPoint(event);
        pickPendingId=root.crypto?.randomUUID?.()||String(Date.now());colorBusy=true;pendingColor=undefined;renderColor();
        const request={id:pickPendingId,x,y,width:ui.kcfCanvas.width,height:ui.kcfCanvas.height,stamp:kcfImageStamp,...(caseId==='02_04_color'?{mode:'box'}:{})};
        try{context.publish(COLOR_PICK,{data:JSON.stringify(request)});ui.colorReply.textContent='已提交点击位置，等待104锁定颜色目标…';}
        catch(error){colorBusy=false;pickPendingId=undefined;renderColor();ui.colorReply.textContent='取色发送失败：'+error.message;return;}
        clearTimeout(pickTimer);const id=pickPendingId;pickTimer=setTimeout(()=>{if(pickPendingId===id){pickPendingId=undefined;colorBusy=false;renderColor();ui.colorReply.textContent='取色请求未收到确认，请检查案例与连接';}},5000);
        return;
      }
      event.preventDefault();kcfDrag=kcfPoint(event);ui.kcfCanvas.setPointerCapture?.(event.pointerId);
    };
    ui.kcfCanvas.onpointermove=event=>{if(kcfDrag)drawKcfBox(kcfPoint(event));};
    ui.kcfCanvas.onpointerup=event=>{
      if(!kcfDrag)return;
      const end=kcfPoint(event);drawKcfBox(end);
      const x=Math.round(Math.min(kcfDrag[0],end[0])),y=Math.round(Math.min(kcfDrag[1],end[1]));
      const width=Math.min(ui.kcfCanvas.width-x,Math.round(Math.abs(end[0]-kcfDrag[0])));
      const height=Math.min(ui.kcfCanvas.height-y,Math.round(Math.abs(end[1]-kcfDrag[1])));
      kcfDrag=undefined;ui.kcfCanvas.releasePointerCapture?.(event.pointerId);
      if(width<=1||height<=1){ui.kcfReply.textContent='选框太小，请框住物体。';return;}
      const scale=(kcfSourceWidth||ui.kcfCanvas.width)/ui.kcfCanvas.width;
      const roi={x_offset:Math.round(x*scale),y_offset:Math.round(y*scale),width:Math.round(width*scale),height:Math.round(height*scale),do_rectify:false};
      try{context.publish(KCF_ROI,roi);ui.kcfReply.textContent=`已提交选框 (${x},${y}) ${width}×${height}，等待104锁定。`;}
      catch(error){ui.kcfReply.textContent='选框发送失败：'+error.message;}
    };
    ui.kcfCanvas.onpointercancel=()=>{kcfDrag=undefined;};
    ui.kcfDistance.oninput=()=>{kcfDistanceEdited=true;ui.kcfDistanceNumber.value=ui.kcfDistance.value;};
    ui.kcfDistanceNumber.oninput=()=>{kcfDistanceEdited=true;if(ui.kcfDistanceNumber.validity.valid)ui.kcfDistance.value=ui.kcfDistanceNumber.value;};
    ui.kcfApplyDistance.onclick=async()=>{
      const value=Number(ui.kcfDistanceNumber.value);
      if(!ui.kcfDistanceNumber.value||!ui.kcfDistanceNumber.validity.valid||!Number.isFinite(value)){ui.kcfDistanceReply.textContent='请输入有效的跟随距离（米）';return;}
      kcfPendingDistance=value;ui.kcfDistanceReply.textContent='已提交，等待跟随控制器读回…';
      try{
        const reply=await callFollowService(follower+'/set_parameters',{parameters:[{name:'target_distance',value:{type:3,bool_value:false,integer_value:0,double_value:value,string_value:'',byte_array_value:[],bool_array_value:[],integer_array_value:[],double_array_value:[],string_array_value:[]}}]});
        if(!reply.results?.length||reply.results.some(result=>!result.successful))throw Error(reply.results?.map(result=>result.reason).filter(Boolean).join('; ')||'控制器未接受距离参数');
      }catch(error){kcfPendingDistance=undefined;ui.kcfDistanceReply.textContent='修改失败：'+error.message;}
    };
    ui.kcfDistance.onchange=()=>ui.kcfApplyDistance.click();
    ui.kcfDistanceNumber.onkeydown=event=>{if(event.key==='Enter'){event.preventDefault();ui.kcfApplyDistance.click();}};
    if(ui.rangeSource)ui.rangeSource.onchange=async()=>{
      const value=ui.rangeSource.value;ui.rangeSourceReply.textContent='正在切换测距来源…';
      try{
        const reply=await callFollowService('/course_apriltag/set_parameters',{parameters:[{name:'distance_source',value:{type:4,bool_value:false,integer_value:0,double_value:0,string_value:value,byte_array_value:[],bool_array_value:[],integer_array_value:[],double_array_value:[],string_array_value:[]}}]});
        if(!reply.results?.length||reply.results.some(r=>!r.successful))throw Error(reply.results?.map(r=>r.reason).join('; ')||'参数未接受');
        ui.rangeSourceReply.textContent='已提交，等待识别节点读回…';
      }catch(error){ui.rangeSourceReply.textContent='切换失败：'+error.message;}
    };
    context.watch('currentFrame');
    const colorTopic=caseId==='02_04_color'?'/vision/color/result':'/vision/detections';
    const markerTracks=marker?'/vision/'+marker+'/tracks':null;
    context.subscribe([KCF_STATUS,...(body?[]:color?[colorTopic]:marker?['/vision/'+marker+'/result',markerTracks]:['/vision/nanotrack/selected']),STATUS].map(topic=>({topic})));
    ui.kcfPicker.insertBefore(sharedRgb,ui.kcfCanvas);
    sharedRgb.addEventListener('rgb-frame',syncRgb);
    syncRgb();
    context.onRender=(state,done)=>{
      try{for(const event of state.currentFrame||[]){
          if(event.topic===STATUS){
            const manager=JSON.parse(event.message.data);
            if(manager.case_id===caseId&&['ERROR','COMPLETED'].includes(manager.phase)||!manager.case_id&&manager.phase==='STOPPED'){
              caseReady=true;
              syncRgb();
            }
            if(manager.case_id===caseId&&['STARTING','STOPPING','ERROR','COMPLETED'].includes(manager.phase))ui.kcfReply.textContent=({STARTING:'正在104启动跟踪…',STOPPING:'正在停止跟随…',ERROR:'跟踪启动错误',COMPLETED:'跟踪进程已结束'})[manager.phase];
            else if(!manager.case_id&&['STOPPED','IDLE'].includes(manager.phase))ui.kcfReply.textContent='目标追踪案例已停止';
            else if(manager.case_id&&manager.case_id!==caseId)ui.kcfReply.textContent='目标物跟随未运行；当前案例 '+manager.case_id;
          }
          if(event.topic==='/vision/nanotrack/selected')kcfStopReason=JSON.parse(event.message.data).tracking_stop_reason||'';
          if(color&&event.topic===colorTopic){
            const value=JSON.parse(event.message.data);if(typeof value.selected_color==='string')detectorColor=value.selected_color;detectorSample=value.picked_color;setOverlay(value,value.detections);
            const reply=value.pick_result;
            if(reply&&reply.id===pickPendingId){
              clearTimeout(pickTimer);pickPendingId=undefined;colorBusy=false;
              if(reply.success){pendingColor=reply.selected_color;ui.colorReply.textContent=reply.op==='clear'?'已提交清除，等待读回停车与全部颜色检测状态…':reply.source_color?'已选中'+colorLabel(reply.source_color)+'目标，等待跟随确认…':'已从RGB取色，等待跟随颜色确认…';}
              else ui.colorReply.textContent='取色失败：'+reply.message;
            }
            renderColor();
          }
          if(markerTracks&&event.topic===markerTracks){const value=JSON.parse(event.message.data);setOverlay(value,value.tracks);}
          if(marker&&event.topic==='/vision/'+marker+'/result'){
            const value=JSON.parse(event.message.data);
            if(ui.rangeSource&&value.distance_source){ui.rangeSource.value=value.distance_source;ui.rangeSourceReply.textContent='当前来源：'+(value.distance_source==='rgb'?'RGB位姿估距':'配准深度采样')+'（节点读回）';}
          }
          if(event.topic===KCF_STATUS){
            const kcf=JSON.parse(event.message.data);
            caseReady=true;
            syncRgb();
            if(body){
              setOverlay(kcf,kcf.tracks);
              const distance=kcf.person_range_m;
              ui.kcfReply.textContent='人体手势跟随 · '+(kcf.body_tracking?.motion_state??kcf.follow_control_state??kcf.state??'等待目标')+
                (Number.isFinite(distance)?' · '+distance.toFixed(2)+' m':'');
              continue;
            }
            if(!color&&!marker)setOverlay(kcf,kcf.tracks);
            if(color&&typeof kcf.class_filter==='string'){controllerColor=kcf.class_filter;renderColor();}
            if(typeof kcf.enable_motion==='boolean'){
              kcfMotion=kcf.enable_motion;
              if(kcfPendingMotion===kcfMotion){kcfPendingMotion=undefined;ui.kcfMotionReply.textContent=kcfMotion?'已开启底盘跟随（控制器读回）':'已关闭底盘跟随，目标框和ID保留（控制器读回）';}
              renderMotion();
            }
            if(Number.isFinite(kcf.target_distance_m)){
              const value=kcf.target_distance_m;ui.kcfActualDistance.textContent=value.toFixed(2)+' m（控制器读回'+(kcf.distance_persistent?' · 已永久保存':'')+'）';
              if(kcfPendingDistance!==undefined&&Math.abs(value-kcfPendingDistance)<1e-6){
                if(kcf.distance_persistent){kcfPendingDistance=undefined;kcfDistanceEdited=false;ui.kcfDistanceReply.textContent='已生效并永久保存：'+value.toFixed(2)+' m';}
                else ui.kcfDistanceReply.textContent='距离已生效，等待104永久保存确认…';
              }
              if(!kcfDistanceEdited){ui.kcfDistance.value=ui.kcfDistanceNumber.value=value;}
            }
            kcfSourceWidth=kcf.image_width||kcfSourceWidth;const labels={FOLLOW:'前进跟随',BACKOFF:'后退保持距离',HOLD:'距离合适，保持',ALIGN:'转向对准物体',WAIT_DEPTH:'等待有效深度',LOST:kcfStopReason==='template_mismatch'?'原目标模板不匹配，已停止并保留原目标':'等待框选目标'};
            ui.kcfReply.textContent=(color?'颜色跟随':marker?marker.toUpperCase()+' / KCF':kcf.tracker_backend==='nanotrack'?'NanoTrack':'KCF')+(kcf.tracking_runtime&&kcf.tracking_runtime!=='unknown'?' · '+kcf.tracking_runtime:'')+' · '+(color&&kcf.class_filter==='__click_target__'?'等待点击颜色检测框':(marker||color)&&kcf.motion_state==='LOST'?'等待识别目标':labels[kcf.motion_state]||kcf.motion_state)+' · ID '+(kcf.locked_id??'无')+(kcf.depth_m!=null?' · '+Number(kcf.depth_m).toFixed(2)+' m':'')+(kcf.enable_motion?' · 实机跟随':' · 识别演示，运动关闭');
          }
      }}catch(error){ui.kcfReply.textContent='追踪窗口错误：'+error.message;}finally{done();}
    };
    return ()=>{context.subscribe([]);context.unadvertise?.(CONTROL);context.unadvertise?.(KCF_ROI);if(color)context.unadvertise?.(COLOR_PICK);clearTimeout(pickTimer);sharedRgb?.removeEventListener('rgb-frame',syncRgb);context.onRender=undefined;el.remove();};
  }

  function register() {
    let attempts=0;
    const timer=setInterval(()=>{
      const fiber=document.getElementById('root')?._reactRootContainer?.current;
      const stack=fiber?[fiber]:[],seen=new Set();let catalog;
      while(stack.length&&!catalog){const f=stack.pop();if(!f||seen.has(f))continue;seen.add(f);const values=[f.memoizedProps?.value];let d=f.dependencies?.firstContext;while(d){values.push(d.memoizedValue);d=d.next;}for(const v of values)if(v&&typeof v.getState==='function'&&typeof v.getState().installExtension==='function'){catalog=v;break;}stack.push(f.child,f.sibling);}
      if(!catalog){if(++attempts>150)clearInterval(timer);return;}
      const name='local.omnifleet-vision';
      const install=()=>{const state=catalog.getState();if(state.installedPanels?.[name+'.demo']?.registration?.initPanel===initPanel&&state.installedPanels?.[name+'.kcf']?.registration?.initPanel===initKcfPanel)return;catalog.setState({installedExtensions:[...(state.installedExtensions||[]).filter(item=>item.id!==name),{id:name,qualifiedName:name,namespace:'local',name:'omnifleet-vision',publisher:'local',version:'1.0.0',displayName:'104 视觉案例演示',main:'./vision-demo-panel.js'}],installedPanels:{...state.installedPanels,[name+'.demo']:{extensionName:name,extensionNamespace:'local',registration:{name:'demo',initPanel}},[name+'.kcf']:{extensionName:name,extensionNamespace:'local',registration:{name:'kcf',initPanel:initKcfPanel}}}});};
      catalog.subscribe(install);install();clearInterval(timer);
    },200);
  }
  if(typeof module!=='undefined'&&module.exports)module.exports={initPanel,initKcfPanel};else register();
})(typeof window!=='undefined'?window:globalThis);

