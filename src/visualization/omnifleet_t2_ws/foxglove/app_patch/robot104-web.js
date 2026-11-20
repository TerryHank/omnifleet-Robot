(() => {
  const url = new URL(location.href);
  const defaults = {
    ds: "foxglove-websocket",
    "ds.url": "ws://" + url.hostname + ":8765",
    omnifleetProfile: "robot_104",
  };
  for (const [key, value] of Object.entries(defaults)) {
    if (!url.searchParams.has(key)) url.searchParams.set(key, value);
  }
  history.replaceState(history.state, "", url);
  globalThis.global = globalThis;
  globalThis.FOXGLOVE_STUDIO_DEFAULT_LAYOUT = {"configById":{"local.omnifleet-113-panels.nav2-hot-params-panel!nav2HotParams":{"foxglovePanelTitle":"104 导航参数与启动","fontScale":1.4,"collapsedSections":{"group:全局与局部代价地图共用":false,"advanced:hot_dwb":true,"algorithm:global":true,"algorithm:local":true,"group:导航行为":true,"group:MOLA 点云转地图（地图坐标系 Z，非局部障碍过滤）":false,"sub:rpp:速度与平顺":false,"sub:rpp:避障与路线选择":false,"sub:rpp:路线跟踪":false,"sub:rpp:先转向再走":false,"sub:hot_dwb:走不通时怎么处理":false,"sub:mppi:避障与路线选择":false,"sub:mppi:到点与终点对齐":false,"sub:mppi:走不通时怎么处理":false,"sub:mppi:速度与平顺":false,"group:建图与避障共用高度（地图坐标系 Z）":true}},"3D!navigation104":{"cameraState":{"perspective":true,"distance":11.663507799812695,"phi":0.0000573237639305409,"thetaOffset":-147.7761416136201,"targetOffset":[-2.953989884811477,0.41093792884007896,-6.689685961048182e-16],"target":[0,0,0],"targetOrientation":[0,0,0,1],"fovy":45,"near":0.1,"far":5000},"followMode":"follow-pose","followTf":"map","scene":{"transforms":{"showLabel":false,"axisScale":0.5,"lineWidth":1,"enablePreloading":true},"meshUpAxis":"z_up"},"transforms":{"frame:map":{"visible":true}},"topics":{"/map":{"visible":true,"colorMode":"custom","minColor":"#c2cbd880","maxColor":"#596c8580","unknownColor":"#ffffff00"},"/global_costmap/costmap":{"visible":true,"colorMode":"custom","minColor":"#fff2cc00","maxColor":"#e9ad5a3d","unknownColor":"#ffffff00"},"/local_costmap/costmap":{"visible":true,"colorMode":"custom","minColor":"#ffffff00","maxColor":"#f27b854d","unknownColor":"#ffffff00"},"/global_costmap/published_footprint":{"visible":true,"color":"#ffd600","lineWidth":0.012},"/local_costmap/published_footprint":{"visible":true,"color":"#ff1744","lineWidth":0.02},"/lookahead_collision_arc":{"visible":true,"color":"#ff9100","lineWidth":0.015},"/lookahead_point":{"visible":true,"color":"#00e676"},"/plan":{"visible":true,"color":"#23b5e6ff","lineWidth":0.045},"/local_plan":{"visible":true,"color":"#ff54dfff","lineWidth":0.075},"/robot_description":{"visible":true},"/set_pose":{"visible":true},"/initialpose":{"visible":true},"/goal_pose":{"visible":true},"/lidar_odometry/localmap_points":{"visible":false,"colorField":"z","colorMode":"colormap","colorMap":"turbo"},"/lidar_odometry/nav_voxelmap_points":{"visible":false,"colorField":"z","colorMode":"colormap","colorMap":"turbo"},"/rslidar_points":{"visible":false,"frameLocked":false,"pointSize":2.5,"pointShape":"circle","decayTime":1.5,"colorMode":"colormap","colorField":"intensity","colorMap":"turbo","minValue":0,"maxValue":255},"/received_global_plan":{"visible":false,"color":"#ffe600","lineWidth":0.04},"/unsmoothed_plan":{"visible":false,"color":"#ff9100","lineWidth":0.025},"/omnifleet_t2/waypoints/add_pose":{"visible":true},"/omnifleet_t2/waypoints/markers":{"visible":true},"/omnifleet_t2/waypoints/path":{"visible":true,"color":"#4499ffaa","lineWidth":0.035},"/cost_cloud":{"visible":false},"/omnifleet_t2/waypoints/active_path":{"visible":true,"color":"#00ff66","lineWidth":0.065},"/navigation/peer_map":{"visible":false},"/fleet/alignment_points":{"visible":false,"colorField":"z","colorMode":"colormap","colorMap":"turbo","pointSize":5.2},"/transformed_global_plan":{"visible":false,"color":"#ff55cc","lineWidth":0.045},"/navigation/deskewed_points":{"visible":false,"pointSize":2,"colorMode":"colormap","colorField":"z","colorMap":"turbo"},"/trajectories":{"visible":true,"color":"#ff54dfff","showOutlines":false,"namespaces":{"Candidate Trajectories":{"visible":false},"Optimal Trajectory":{"visible":true}}}},"layers":{"requiredSensorsGrid":{"layerId":"foxglove.Grid","visible":true,"frameLocked":true,"label":"odom 地面网格","frameId":"map","size":20,"divisions":20,"lineWidth":1,"color":"#7187a04d","position":[0,0,0],"rotation":[0,0,0]},"omnifleetT2RobotModel":{"layerId":"foxglove.Urdf","visible":true,"frameLocked":true,"label":"Ranger Mini 3.0 四驱四转","instanceId":"omnifleetT2RobotModel","sourceType":"topic","framePrefix":"","displayMode":"visual","fallbackColor":"#9e9e9e","order":1,"topic":"/robot_description"}},"publish":{"type":"pose","poseTopic":"/goal_pose","pointTopic":"/navigation/goal_point","poseEstimateTopic":"/initialpose","poseEstimateXDeviation":0.5,"poseEstimateYDeviation":0.5,"poseEstimateThetaDeviation":0.26179939},"imageMode":{},"foxglovePanelTitle":"104 导航 · 地图 / 全局路径 / 局部轨迹"},"Gauge!angular104":{"path":"/rslidar_imu_data_corrected.angular_velocity.z","minValue":-1,"maxValue":1,"colorMode":"gradient","colorMap":"red-yellow-green","gradient":["#2196f3","#ff9800"],"reverse":false,"foxglovePanelTitle":"104 IMU 角速度 Z · rad/s"},"RawMessages!battery104":{"topicPath":"/voltage.data","expansion":"all","fontSize":32,"foxglovePanelTitle":"104 电池电压","diffEnabled":false,"diffMethod":"custom","diffTopicPath":"","showFullMessageForDiff":false},"Teleop!manual104":{"topic":"/cmd_vel","publishRate":10,"upButton":{"field":"linear-x","value":0.15},"downButton":{"field":"linear-x","value":-0.15},"leftButton":{"field":"angular-z","value":1},"rightButton":{"field":"angular-z","value":-1},"foxglovePanelTitle":"104 履带手动控制","stopOnRelease":true}},"globalVariables":{},"userNodes":{},"playbackConfig":{"speed":1},"layout":{"first":"local.omnifleet-113-panels.nav2-hot-params-panel!nav2HotParams","second":{"direction":"row","splitPercentage":69.81132075471699,"first":{"direction":"column","splitPercentage":64.25531914893618,"first":"3D!navigation104","second":"Gauge!angular104"},"second":{"direction":"column","splitPercentage":15,"first":"RawMessages!battery104","second":"Teleop!manual104"}},"direction":"row","splitPercentage":24.81081081081081}};

  function replacePanelInLayout(layout, oldId, newId) {
    const replace = node => node === oldId ? newId
      : node && typeof node === "object" ? {...node, first: replace(node.first), second: replace(node.second)}
      : node;
    layout.layout = replace(layout.layout);
    for (const config of Object.values(layout.configById)) {
      for (const tab of config?.tabs ?? []) tab.layout = replace(tab.layout);
    }
  }

  function migrateSpeedGauge(layout) {
    const oldId = "Gauge!angular104";
    const gauge = layout?.configById?.[oldId];
    if (gauge?.path !== "/odom.twist.twist.linear.x" &&
        gauge?.path !== "/rslidar_imu_data_corrected.angular_velocity.z") return false;

    const newId = "local.omnifleet-113-panels.speed-gauge!speed104";
    replacePanelInLayout(layout, oldId, newId);
    layout.configById[newId] = {foxglovePanelTitle: "底盘速度 · m/s"};
    delete layout.configById[oldId];
    return true;
  }

  migrateSpeedGauge(globalThis.FOXGLOVE_STUDIO_DEFAULT_LAYOUT);
  const speedGaugeVersionKey = "omnifleet.robot104.speedGaugeVersion";
  if (localStorage.getItem(speedGaugeVersionKey) !== "2") {
    const saved = localStorage.getItem("studio.layout");
    if (saved) {
      let layout;
      try { layout = JSON.parse(saved); } catch { /* Foxglove owns layout recovery. */ }
      if (migrateSpeedGauge(layout)) {
        localStorage.setItem("studio.layout", JSON.stringify(layout));
      }
    }
    localStorage.setItem(speedGaugeVersionKey, "2");
  }

  function migrateDriveJoystick(layout) {
    const oldId = "Teleop!manual104";
    const previous = layout?.configById?.[oldId];
    if (!previous) return false;
    const newId = "local.omnifleet-113-panels.drive-joystick!manual104";
    const limit = (button, field, fallback) => button?.field === field && Number.isFinite(button.value)
      ? Math.abs(button.value) : fallback;
    replacePanelInLayout(layout, oldId, newId);
    layout.configById[newId] = {
      foxglovePanelTitle: "履带手动摇杆",
      topic: previous.topic ?? "",
      publishRate: previous.publishRate ?? 10,
      forward: limit(previous.upButton, "linear-x", 0.15),
      reverse: limit(previous.downButton, "linear-x", 0.15),
      left: limit(previous.leftButton, "angular-z", 1),
      right: limit(previous.rightButton, "angular-z", 1),
    };
    delete layout.configById[oldId];
    return true;
  }

  migrateDriveJoystick(globalThis.FOXGLOVE_STUDIO_DEFAULT_LAYOUT);
  const joystickVersionKey = "omnifleet.robot104.joystickVersion";
  if (localStorage.getItem(joystickVersionKey) !== "1") {
    const saved = localStorage.getItem("studio.layout");
    if (saved) {
      let layout;
      try { layout = JSON.parse(saved); } catch { /* Foxglove owns layout recovery. */ }
      if (migrateDriveJoystick(layout)) {
        localStorage.setItem("studio.layout", JSON.stringify(layout));
      }
    }
    localStorage.setItem(joystickVersionKey, "1");
  }

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
    layout.configById[newId] = {foxglovePanelTitle: "104 电池电压"};
    delete layout.configById[oldId];
    return true;
  }
  migrateBattery(globalThis.FOXGLOVE_STUDIO_DEFAULT_LAYOUT);

  function migrateRangerDrive(layout) {
    const config = layout?.configById;
    for (const panel of Object.values(config || {})) {
      if (panel?.publish?.pointTopic === "/clicked_point") panel.publish.pointTopic = "/navigation/goal_point";
    }
    const old = "Teleop!manual104";
    const tab = "Tab!rangerDrive104";
    const id = "local.omnifleet-113-panels.ranger-drive!manual104";
    if (config?.[id]) return false;
    const original=config?.[old] || config?.["local.omnifleet-113-panels.drive-joystick!manual104"];
    if (!original) return false;
    let found = false;
    const replace = node => {
      if (node === old || node === tab || node === "local.omnifleet-113-panels.drive-joystick!manual104") {
        found = true;
        return id;
      }
      return node && typeof node === "object"
        ? {...node, first: replace(node.first), second: replace(node.second)}
        : node;
    };
    layout.layout = replace(layout.layout);
    for (const [key, panel] of Object.entries(config)) {
      if (key !== tab && Array.isArray(panel?.tabs)) {
        for (const item of panel.tabs) item.layout = replace(item.layout);
      }
    }
    if (!found) return false;
    const drive = original;
    config[id] = {foxglovePanelTitle: "104 运动控制",
      forward: drive.upButton?.value, reverse: drive.downButton?.value,
      spinLeft: drive.leftButton?.value, spinRight: drive.rightButton?.value};
    for (const key of [old, tab, "local.omnifleet-113-panels.drive-joystick!manual104", "Teleop!rangerSlide104", "Teleop!rangerWheelAngle104"]) delete config[key];
    return true;
  }

  migrateRangerDrive(globalThis.FOXGLOVE_STUDIO_DEFAULT_LAYOUT);
  const savedDriveLayout = localStorage.getItem("studio.layout");
  if (savedDriveLayout) {
    let layout;
    try { layout = JSON.parse(savedDriveLayout); } catch { /* Foxglove owns layout recovery. */ }
    if (migrateRangerDrive(layout)) localStorage.setItem("studio.layout", JSON.stringify(layout));
  }

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
  function migrateDisplayClouds(layout) {
    const replacements = {
      "/navigation/deskewed_points": "/visualization/web/deskewed_points",
      "/visualization/slam_points_below_1m": "/visualization/web/slam_points_below_1m",
      "/visualization/local_obstacle_points": "/visualization/web/local_obstacle_points",
    };
    let changed = false;
    for (const [id, panel] of Object.entries(layout?.configById ?? {})) {
      if (!id.startsWith("3D!") || !panel.topics) continue;
      for (const [original, compact] of Object.entries(replacements)) {
        const options = panel.topics[original];
        if (!options) continue;
        panel.topics[compact] ??= options;
        delete panel.topics[original];
        changed = true;
      }
    }
    return changed;
  }

  const cloudVersionKey = "omnifleet.robot104.pointCloudDisplayVersion";
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
    localStorage.removeItem("omnifleet.robot104.singleNavCloudVersion");
  }

  if (url.searchParams.get("ds") === defaults.ds && url.searchParams.get("ds.url") === defaults["ds.url"]) {
    migrateDisplayClouds(globalThis.FOXGLOVE_STUDIO_DEFAULT_LAYOUT);
    const saved = localStorage.getItem("studio.layout");
    if (saved) {
      let layout;
      try { layout = JSON.parse(saved); } catch { /* Foxglove owns layout recovery. */ }
      if (migrateDisplayClouds(layout)) {
        localStorage.setItem("studio.layout", JSON.stringify(layout));
      }
    }
  }
})();
