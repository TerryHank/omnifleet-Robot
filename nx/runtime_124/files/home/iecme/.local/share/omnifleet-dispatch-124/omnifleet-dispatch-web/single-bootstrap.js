(() => {
  const panel = document.currentScript;
  const page = new URL(location.href);
  const bridge = new URL(page);
  bridge.protocol = page.protocol === 'https:' ? 'wss:' : 'ws:';
  bridge.port = '8765';
  bridge.pathname = '/';
  bridge.search = '';
  bridge.hash = '';
  const supplied = page.searchParams.get('ds.url');
  let source = supplied ?? bridge.origin;
  try {
    const selected = new URL(source);
    const onDefaultBridge = selected.origin === bridge.origin && selected.pathname === '/';
    if (window.OmniFleetCloudDecoderReady && (!supplied || onDefaultBridge)) {
      const cloudBridge = new URL('/single-cloud-socket', page);
      cloudBridge.protocol = bridge.protocol;
      source = cloudBridge.href;
    }
  } catch {
    // Preserve the explicitly supplied source so the existing connection error can explain it.
  }
  page.searchParams.set('ds', 'foxglove-websocket');
  page.searchParams.set('ds.url', source);
  page.searchParams.set('omnifleetProfile', 'single');
  history.replaceState(history.state, '', page);
  window.global = window;

  // Use the navigation topic to distinguish a vehicle namespace from unrelated map layers.
  function discoverNamespace() {
    return new Promise(resolve => {
      const navigation = new Set();
      const maps = new Set();
      let socket;
      let timer;
      let finished = false;
      function finish() {
        if (finished) return;
        finished = true;
        clearTimeout(timer);
        const candidates = [...navigation].filter(namespace => maps.has(namespace));
        resolve(candidates.length === 1 ? candidates[0] : navigation.size === 1 ? [...navigation][0] : undefined);
        socket?.close();
      }
      try {
        socket = new WebSocket(source, ['foxglove.sdk.v1', 'foxglove.websocket.v1']);
      } catch {
        finish();
        return;
      }
      timer = setTimeout(finish, 1800);
      socket.addEventListener('message', ({data}) => {
        if (typeof data !== 'string') return;
        const message = JSON.parse(data);
        if (message.op !== 'advertise') return;
        for (const {topic, schemaName} of message.channels) {
          if (schemaName === 'std_msgs/msg/String' && topic.endsWith('/navigation/status')) {
            navigation.add(topic.slice(0, -'/navigation/status'.length));
          }
          if (schemaName === 'nav_msgs/msg/OccupancyGrid' && topic.endsWith('/map')) {
            maps.add(topic.slice(0, -'/map'.length));
          }
        }
        if (navigation.size === 1 && maps.has([...navigation][0])) finish();
      });
      socket.addEventListener('error', finish);
      socket.addEventListener('close', finish);
    });
  }

  // The local 124 bridge exposes unprefixed navigation and map topics.
  // Probe only when the operator connects this page to a different data source.
  const viaCloud = new URL('/single-cloud-socket', page);
  viaCloud.protocol = bridge.protocol;
  const localSource = source === bridge.origin || source === bridge.href || source === viaCloud.href;

  function restoreAckermannControls(data) {
    const prefix = 'local.omnifleet-single-panels.';
    const joystick = prefix + 'drive-joystick!manual';
    const config = data?.configById;
    if (config?.[joystick]?.foxglovePanelTitle !== '履带手动摇杆' ||
        !JSON.stringify(data.layout).includes(JSON.stringify(joystick))) return data;
    config[joystick].foxglovePanelTitle = '124 阿克曼摇杆';
    const cards = [
      [prefix+'drive-speed!driveSpeed124','124 行驶速度',14],
      [prefix+'steering-center!steeringCenter124','124 舵机零点偏置',20],
      [prefix+'steering-limit!steeringLimit124','124 最大转向角度',24],
    ];
    let branch = joystick;
    for (const [id,title,percentage] of cards.reverse()) {
      if (config[id]) continue;
      config[id] = {foxglovePanelTitle:title};
      branch = {direction:'column',splitPercentage:percentage,first:id,second:branch};
    }
    function replaceJoystick(node) {
      if (node === joystick) return branch;
      if (!node || typeof node !== 'object') return node;
      return {...node,first:replaceJoystick(node.first),second:replaceJoystick(node.second)};
    }
    data.layout = replaceJoystick(data.layout);
    const publish = config['3D!navigation']?.publish;
    if (publish?.pointTopic?.replace(/^\//,'') === 'clicked_point') publish.type = 'point';
    return data;
  }

  const namespaceReady = localSource ? Promise.resolve('') : discoverNamespace();
  namespaceReady.then(namespace => {
    const topic = name => namespace === undefined ? '' : namespace + '/' + name.replace(/^\//, '');
    const layout = window.OmniFleetSingleLayout;
    if (localSource) restoreAckermannControls(layout);
    for (const config of Object.values(layout.configById)) {
      if (config.topics) {
        config.topics = namespace === undefined ? {} : Object.fromEntries(
          Object.entries(config.topics).map(([name, options]) => [topic(name), options]),
        );
      }
      if (config.topic) config.topic = topic(config.topic);
      for (const layer of Object.values(config.layers ?? {})) {
        if (layer.topic) layer.topic = topic(layer.topic);
      }
      for (const key of ['poseTopic', 'pointTopic', 'poseEstimateTopic']) {
        if (config.publish?.[key]) config.publish[key] = topic(config.publish[key]);
      }
    }
    window.FOXGLOVE_STUDIO_DEFAULT_LAYOUT = layout;

    // Keep legacy saved layouts out of the neutral page and scope future edits by data source.
    for (const method of ['getItem', 'setItem', 'removeItem']) {
      const original = Storage.prototype[method];
      Storage.prototype[method] = function(key, ...args) {
        if (this === localStorage && key === 'studio.layout') {
          key = 'omnifleet.single.layout:' + source + ':' + (namespace ?? 'unavailable');
          if (localSource && method === 'getItem') {
            const saved = original.call(this, key);
            try {
              const data = JSON.parse(saved);
              if (data?.configById?.['local.omnifleet-single-panels.drive-joystick!manual']?.foxglovePanelTitle === '履带手动摇杆') {
                const fixed = JSON.stringify(restoreAckermannControls(data));
                this.setItem(key, fixed);
                return fixed;
              }
            } catch {
              // Leave layout recovery to Foxglove if the saved document is invalid.
            }
            return saved;
          }
        }
        return original.call(this, key, ...args);
      };
    }

    // Adapt the reusable panels' logical ROS paths at the connection boundary.
    window.OmniFleetSingle = {
      topic,
      waypointTopics: localSource ? [topic('omnifleet_a2/waypoints/catalog'), topic('navigation/status')] : undefined,
      bindPanel(init) {
        return context => init(new Proxy(context, {
          get(target, property) {
            if (property === 'subscribe') {
              return subscriptions => target.subscribe(namespace === undefined ? [] : subscriptions.map(
                item => ({...item, topic: topic(item.topic)}),
              ));
            }
            if (['advertise', 'unadvertise', 'publish', 'callService'].includes(property)) {
              if (!target[property]) return undefined;
              return (name, ...args) => {
                if (namespace === undefined) {
                  if (property === 'callService') return Promise.reject(new Error('当前数据源尚未找到车辆命名空间'));
                  return undefined;
                }
                return target[property](topic(name), ...args);
              };
            }
            const value = target[property];
            return typeof value === 'function' ? value.bind(target) : value;
          },
          set(target, property, value) {
            target[property] = property === 'onRender' && value && namespace ? (state, done) => {
              const logicalName = name => name.startsWith(namespace + '/') ? name.slice(namespace.length) : name;
              value({
                ...state,
                topics: state.topics?.map(entry => ({...entry, name: logicalName(entry.name)})),
                currentFrame: state.currentFrame?.map(event => ({...event, topic: logicalName(event.topic)})),
              }, done);
            } : value;
            return true;
          },
        }));
      },
    };

    for (const path of ['single-waypoints.js', panel.dataset.bundle, 'single-panels.js', 'foxglove-tour.js']) {
      const script = document.createElement('script');
      script.async = false;
      script.src = new URL(path, page).href;
      document.head.append(script);
    }
  });
})();
