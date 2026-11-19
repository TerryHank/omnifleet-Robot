(() => {
  const panel = document.currentScript;
  const page = new URL(location.href);
  const bridge = new URL(page);
  bridge.protocol = page.protocol === 'https:' ? 'wss:' : 'ws:';
  bridge.port = '8765';
  bridge.pathname = '/';
  bridge.search = '';
  bridge.hash = '';
  const source = page.searchParams.get('ds.url') ?? bridge.origin;
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

  discoverNamespace().then(namespace => {
    const topic = name => namespace === undefined ? '' : namespace + '/' + name.replace(/^\//, '');
    const layout = window.OmniFleetSingleLayout;
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
        }
        return original.call(this, key, ...args);
      };
    }

    // Adapt the reusable panels' logical ROS paths at the connection boundary.
    window.OmniFleetSingle = {
      topic,
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
