(() => {
  const url = new URL(location.href);
  const defaults = {
    ds: "foxglove-websocket",
    "ds.url": "ws://" + url.hostname + ":8765",
    omnifleetProfile: "robot_112",
  };
  for (const [key, value] of Object.entries(defaults)) {
    if (!url.searchParams.has(key)) url.searchParams.set(key, value);
  }
  history.replaceState(history.state, "", url);
  globalThis.global = globalThis;
  globalThis.FOXGLOVE_STUDIO_DEFAULT_LAYOUT = {"configById":{"local.omnifleet-113-panels.nav2-hot-params-panel!nav2HotParams":{"foxglovePanelTitle":"124 永久参数调试","fontScale":1.4,"collapsedSections":{"group:全局与局部代价地图共用":false,"advanced:hot_dwb":true,"algorithm:global":true,"algorithm:local":true,"group:导航行为":true,"group:MOLA 点云转地图（地图坐标系 Z，非局部障碍过滤）":false,"sub:rpp:速度与平顺":false,"sub:rpp:避障与路线选择":false,"sub:rpp:路线跟踪":false,"sub:rpp:先转向再走":false,"sub:hot_dwb:走不通时怎么处理":false,"sub:mppi:避障与路线选择":false,"sub:mppi:到点与终点对齐":false,"sub:mppi:走不通时怎么处理":false,"sub:mppi:速度与平顺":false,"group:建图与避障共用高度（地图坐标系 Z）":true}},"3D!navigation104":{"cameraState":{"perspective":true,"distance":11.663507799812695,"phi":0.0000573237639305409,"thetaOffset":-147.7761416136201,"targetOffset":[-2.953989884811477,0.41093792884007896,-6.689685961048182e-16],"target":[0,0,0],"targetOrientation":[0,0,0,1],"fovy":45,"near":0.1,"far":5000},"followMode":"follow-pose","followTf":"map","scene":{"transforms":{"showLabel":false,"axisScale":0.5,"lineWidth":1,"enablePreloading":true},"meshUpAxis":"z_up"},"transforms":{"frame:map":{"visible":true}},"topics":{"/map":{"visible":true,"colorMode":"custom","minColor":"#c2cbd880","maxColor":"#596c8580","unknownColor":"#ffffff00"},"/global_costmap/costmap":{"visible":true,"colorMode":"custom","minColor":"#fff2cc00","maxColor":"#e9ad5a3d","unknownColor":"#ffffff00"},"/local_costmap/costmap":{"visible":true,"colorMode":"custom","minColor":"#ffffff00","maxColor":"#f27b854d","unknownColor":"#ffffff00"},"/global_costmap/published_footprint":{"visible":true,"color":"#ffd600","lineWidth":0.012},"/local_costmap/published_footprint":{"visible":true,"color":"#ff1744","lineWidth":0.02},"/lookahead_collision_arc":{"visible":true,"color":"#ff9100","lineWidth":0.015},"/lookahead_point":{"visible":true,"color":"#00e676"},"/plan":{"visible":true,"color":"#23b5e6ff","lineWidth":0.045},"/local_plan":{"visible":true,"color":"#ff54dfff","lineWidth":0.075},"/robot_description":{"visible":true},"/set_pose":{"visible":true},"/initialpose":{"visible":true},"/goal_pose":{"visible":true},"/lidar_odometry/localmap_points":{"visible":false,"colorField":"z","colorMode":"colormap","colorMap":"turbo"},"/lidar_odometry/nav_voxelmap_points":{"visible":false,"colorField":"z","colorMode":"colormap","colorMap":"turbo"},"/rslidar_points":{"visible":false,"frameLocked":false,"pointSize":2.5,"pointShape":"circle","decayTime":1.5,"colorMode":"colormap","colorField":"intensity","colorMap":"turbo","minValue":0,"maxValue":255},"/received_global_plan":{"visible":false,"color":"#ffe600","lineWidth":0.04},"/unsmoothed_plan":{"visible":false,"color":"#ff9100","lineWidth":0.025},"/omnifleet_a2/waypoints/add_pose":{"visible":true},"/omnifleet_a2/waypoints/markers":{"visible":true},"/omnifleet_a2/waypoints/path":{"visible":true,"color":"#4499ffaa","lineWidth":0.035},"/cost_cloud":{"visible":false},"/omnifleet_a2/waypoints/active_path":{"visible":true,"color":"#00ff66","lineWidth":0.065},"/navigation/peer_map":{"visible":false},"/fleet/alignment_points":{"visible":false,"colorField":"z","colorMode":"colormap","colorMap":"turbo","pointSize":5.2},"/transformed_global_plan":{"visible":false,"color":"#ff55cc","lineWidth":0.045},"/navigation/deskewed_points":{"visible":false,"pointSize":2,"colorMode":"colormap","colorField":"z","colorMap":"turbo"},"/trajectories":{"visible":true,"color":"#ff54dfff","showOutlines":false,"namespaces":{"Candidate Trajectories":{"visible":false},"Optimal Trajectory":{"visible":true}}}},"layers":{"requiredSensorsGrid":{"layerId":"foxglove.Grid","visible":true,"frameLocked":true,"label":"odom 地面网格","frameId":"map","size":20,"divisions":20,"lineWidth":1,"color":"#7187a04d","position":[0,0,0],"rotation":[0,0,0]},"omnifleetT2RobotModel":{"layerId":"foxglove.Urdf","visible":true,"frameLocked":true,"label":"OmniFleet T2履带模型 0.50×0.37×0.33 m","instanceId":"omnifleetT2RobotModel","sourceType":"topic","framePrefix":"","displayMode":"visual","fallbackColor":"#9e9e9e","order":1,"topic":"/robot_description"}},"publish":{"type":"point","poseTopic":"/goal_pose","pointTopic":"/clicked_point","poseEstimateTopic":"/initialpose","poseEstimateXDeviation":0.5,"poseEstimateYDeviation":0.5,"poseEstimateThetaDeviation":0.26179939},"imageMode":{},"foxglovePanelTitle":"122 导航 · 地图 / 全局路径 / 局部轨迹"},"Gauge!angular104":{"path":"/rslidar_imu_data_corrected.angular_velocity.z","minValue":-1,"maxValue":1,"colorMode":"gradient","colorMap":"red-yellow-green","gradient":["#2196f3","#ff9800"],"reverse":false,"foxglovePanelTitle":"122 IMU 角速度 Z · rad/s"},"RawMessages!battery104":{"topicPath":"/voltage.data","expansion":"all","fontSize":32,"foxglovePanelTitle":"122 电池电压","diffEnabled":false,"diffMethod":"custom","diffTopicPath":"","showFullMessageForDiff":false},"Teleop!manual104":{"topic":"/cmd_vel","publishRate":10,"upButton":{"field":"linear-x","value":0.15},"downButton":{"field":"linear-x","value":-0.15},"leftButton":{"field":"angular-z","value":1},"rightButton":{"field":"angular-z","value":-1},"foxglovePanelTitle":"122 履带手动控制","stopOnRelease":true}},"globalVariables":{},"userNodes":{},"playbackConfig":{"speed":1},"layout":{"first":"local.omnifleet-113-panels.nav2-hot-params-panel!nav2HotParams","second":{"direction":"row","splitPercentage":69.81132075471699,"first":{"direction":"column","splitPercentage":64.25531914893618,"first":"3D!navigation104","second":"Gauge!angular104"},"second":{"direction":"column","splitPercentage":15,"first":"RawMessages!battery104","second":"Teleop!manual104"}},"direction":"row","splitPercentage":24.81081081081081}};

  const layout = globalThis.FOXGLOVE_STUDIO_DEFAULT_LAYOUT;
  const driveId = "local.omnifleet-113-panels.ackermann-drive!manual122";
  layout.layout.second.second.second = driveId;
  delete layout.configById["Teleop!manual104"];
  layout.configById[driveId] = { foxglovePanelTitle: "122 阿克曼运动控制" };

  // Display measured point coordinates from the map-frame deskewed cloud.
  const cloudTopics = {
    "/navigation/deskewed_points": {"visible":true,"pointSize":1,"pointShape":"circle","colorMode":"colormap","colorField":"intensity","colorMap":"turbo","decayTime":0},
    "/navigation/height_filtered_points": {"visible":false,"pointSize":1.5,"pointShape":"circle","colorMode":"colormap","colorField":"z","colorMap":"turbo","decayTime":0},
    "/visualization/slam_points_below_1m": {"visible":true,"colorMode":"flat","flatColor":"#ffffffff","pointSize":0.5,"pointShape":"circle","decayTime":0,"frameLocked":true,"colorField":"z"},
    "/rslidar_points": {"visible":false,"pointSize":1.5,"colorMode":"colormap","colorField":"intensity","colorMap":"turbo","pointShape":"circle","decayTime":0,"minValue":0,"maxValue":255},
    "/visualization/local_obstacle_points": {"visible":true,"pointSize":1.5,"colorMode":"colormap","colorField":"z","colorMap":"turbo","minValue":0,"maxValue":2,"pointShape":"circle","decayTime":0},
  };
  function migrateBattery(layout) {
    const oldId = "RawMessages!battery104";
    const newId = "local.omnifleet-113-panels.battery-voltage!battery104";
    if (!layout?.configById?.[oldId]) return false;
    const replace = node => node === oldId ? newId
      : node && typeof node === "object" ? {...node, first: replace(node.first), second: replace(node.second)}
      : node;
    layout.layout = replace(layout.layout);
    layout.configById[newId] = {foxglovePanelTitle: "122 电池电压"};
    delete layout.configById[oldId];
    return true;
  }
  migrateBattery(globalThis.FOXGLOVE_STUDIO_DEFAULT_LAYOUT);

  function applyCloudTopics(layout) {
    const panel = layout?.configById?.["3D!navigation104"];
    if (!panel) return false;
    delete panel.topics?.["/visualization/local_scan_points"];
    panel.topics = { ...panel.topics, ...structuredClone(cloudTopics) };
    return true;
  }

  if (!applyCloudTopics(globalThis.FOXGLOVE_STUDIO_DEFAULT_LAYOUT)) {
    throw new Error("Missing the 104 navigation 3D panel");
  }
  const cloudVersionKey = "omnifleet.robot122.pointCloudDisplayVersion";
  if (localStorage.getItem(cloudVersionKey) !== "1") {
    const saved = localStorage.getItem("studio.layout");
    if (saved) {
      let layout;
      try { layout = JSON.parse(saved); } catch { /* Foxglove owns layout recovery. */ }
      const cloudsUpdated = applyCloudTopics(layout);
      if (migrateBattery(layout) || cloudsUpdated) {
        localStorage.setItem("studio.layout", JSON.stringify(layout));
      }
    }
    localStorage.setItem(cloudVersionKey, "1");
    localStorage.removeItem("omnifleet.robot122.singleNavCloudVersion");
  }

  function addEncoderGauge(data) {
    if (!data || !data.configById) return false;
    const id="local.omnifleet-113-panels.encoder-speed!encoder121";
    if (data.configById[id]) return false;
    const angular="Gauge!angular104";
    let changed=false;
    function insert(node) {
      if(node===angular){changed=true;return {direction:"row",splitPercentage:50,first:angular,second:id};}
      if(node && typeof node==="object")return {...node,first:insert(node.first),second:insert(node.second)};
      return node;
    }
    data.layout=insert(data.layout);
    if(changed)data.configById[id]={foxglovePanelTitle:"121 编码器反馈车速 · m/s"};
    return changed;
  }
  addEncoderGauge(globalThis.FOXGLOVE_STUDIO_DEFAULT_LAYOUT);

  function update124Panels(data) {
    if (!data?.configById) return false;
    let changed = migrateBattery(data);
    const prefix = "local.omnifleet-113-panels.";
    const speed = prefix + "drive-speed!driveSpeed124";
    const center = prefix + "steering-center!steeringCenter124";
    const limit = prefix + "steering-limit!steeringLimit124";
    let added = Boolean(data.configById[speed]);
    function addDriveCards(node) {
      if (node && typeof node === "object") {
        return {...node, first:addDriveCards(node.first), second:addDriveCards(node.second)};
      }
      const kind = typeof node === "string" ? node.split("!",1)[0] : "";
      if (added || (kind !== prefix + "ackermann-drive" && kind !== prefix + "drive-joystick")) return node;
      added = changed = true;
      data.configById[speed] = {foxglovePanelTitle:"124 行驶速度"};
      data.configById[center] = {foxglovePanelTitle:"124 舵机零点偏置"};
      data.configById[limit] = {foxglovePanelTitle:"124 最大转向角度"};
      return {direction:"column",splitPercentage:10,first:speed,second:{
        direction:"column",splitPercentage:17,first:center,second:{
          direction:"column",splitPercentage:20,first:limit,second:node
        }
      }};
    }
    data.layout = addDriveCards(data.layout);
    for (const [id, config] of Object.entries(data.configById)) {
      const kind = id.split("!",1)[0];
      let title;
      if (kind === prefix + "nav2-hot-params-panel") title = "124 永久参数调试";
      if (kind === prefix + "battery-voltage") title = "124 电池电压";
      if (kind === prefix + "drive-joystick" || kind === prefix + "ackermann-drive") {
        title = "124 阿克曼摇杆";
      }
      if (title && config.foxglovePanelTitle !== title) {
        data.configById[id] = {...config, foxglovePanelTitle:title};
        changed = true;
      }
    }
    return changed;
  }
  update124Panels(globalThis.FOXGLOVE_STUDIO_DEFAULT_LAYOUT);
  const existing=localStorage.getItem("studio.layout");
  if(existing) {
    try {
      const saved=JSON.parse(existing);
      const encoderUpdated=addEncoderGauge(saved);
      const pointDefaultVersion = "omnifleet.robot124.positionOnlyPublishDefault";
      let publishUpdated = false;
      if (localStorage.getItem(pointDefaultVersion) !== "1") {
        const publish = saved?.configById?.["3D!navigation104"]?.publish;
        if (publish?.pointTopic === "/clicked_point" && publish.type !== "point") {
          publish.type = "point";
          publishUpdated = true;
        }
        localStorage.setItem(pointDefaultVersion, "1");
      }
      if (update124Panels(saved) || encoderUpdated || publishUpdated) {
        localStorage.setItem("studio.layout", JSON.stringify(saved));
      }
    } catch (_) {}
  }
})();
