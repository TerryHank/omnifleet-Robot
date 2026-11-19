(() => {
  for (const method of ['getItem', 'setItem', 'removeItem']) {
    const original = Storage.prototype[method];
    Storage.prototype[method] = function (key, ...args) {
      const scopedKey = this === localStorage && key === 'studio.layout' ? 'omnifleet.dispatch.onboard.v2' : key;
      return original.call(this, scopedKey, ...args);
    };
  }

  const endpoint = new URL('/dispatch-socket', location.href);
  endpoint.protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
  window.OmniFleetFleetApiBase = location.origin + '/dispatch-api';
  window.OmniFleetFleetWebSocket = endpoint.href;

  const page = new URL(location.href);
  page.searchParams.set('ds', 'foxglove-websocket');
  page.searchParams.set('ds.url', endpoint.href);
  page.searchParams.set('omnifleetProfile', 'fleet');
  page.searchParams.set('demoControl', 'true');
  history.replaceState(null, '', page);
  if (!localStorage.getItem('studio.layout')) {
    localStorage.setItem('studio.layout', JSON.stringify(window.FOXGLOVE_STUDIO_DEFAULT_LAYOUT));
  }
})();
