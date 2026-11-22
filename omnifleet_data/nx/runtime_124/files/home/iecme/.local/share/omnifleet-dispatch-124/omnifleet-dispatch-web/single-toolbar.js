(() => {
  const label = document.getElementById('vehicle-name');
  const trigger = document.getElementById('rename-vehicle');
  const form = document.getElementById('rename-form');
  const input = document.getElementById('vehicle-new-name');
  const status = document.getElementById('rename-status');
  const controls = document.querySelector('.vehicle-toolbar');
  const identity = document.getElementById('vehicle-identity');
  let displayName = '';
  let saving = false;

  function mountHeader() {
    const addPanel = document.getElementById('add-panel-button');
    const toolbar = addPanel?.closest('[data-tourid="app-bar"]')?.firstElementChild;
    const center = toolbar?.children[1];
    if (!center || !toolbar.firstElementChild.contains(addPanel)) return false;
    if (!toolbar.hasAttribute('data-single-vehicle-header')) toolbar.dataset.singleVehicleHeader = '';
    if (!center.hasAttribute('data-single-vehicle-center')) center.dataset.singleVehicleCenter = '';
    if (identity.parentElement !== center) center.prepend(identity);
    if (controls.parentElement !== toolbar.firstElementChild) toolbar.firstElementChild.append(controls);
    identity.hidden = false;
    controls.hidden = false;
    return true;
  }

  mountHeader();
  const observer = new MutationObserver(mountHeader);
  observer.observe(document.getElementById('root'), {childList: true, subtree: true});

  async function fetchState() {
    const response = await fetch('/dispatch-api/state', {cache: 'no-store', signal: AbortSignal.timeout(5000)});
    if (!response.ok) throw new Error('调度服务暂不可用');
    return response.json();
  }

  function updateLabel(state) {
    const id = state.dispatcher_id;
    const assignment = state.assignments?.[id];
    if (!state.ready || !assignment?.robot_name) throw new Error('暂未找到当前车辆');
    displayName = assignment.robot_name;
    label.textContent = displayName;
    return assignment.robot_name;
  }

  function closeForm() {
    form.hidden = true;
    trigger.hidden = false;
    status.textContent = '';
    trigger.setAttribute('aria-expanded', 'false');
    trigger.focus();
  }

  const source = new URLSearchParams(location.search).get('ds.url');
  let sourceHost;
  try {
    sourceHost = source ? new URL(source).hostname : location.hostname;
  } catch {
    status.textContent = '数据源地址无效';
    return;
  }
  if (sourceHost !== location.hostname) {
    status.textContent = '当前数据源连接到其他主机';
    return;
  }

  async function refreshName() {
    try {
      updateLabel(await fetchState());
      trigger.disabled = false;
    } catch (error) {
      status.textContent = error.message;
    }
  }
  void refreshName();
  setInterval(() => {
    if (!document.hidden && form.hidden && !saving) void refreshName();
  }, 3000);

  function openForm() {
    if (trigger.disabled || !form.hidden) return;
    form.hidden = false;
    trigger.hidden = true;
    trigger.setAttribute('aria-expanded', 'true');
    input.value = displayName;
    status.textContent = '';
    input.focus();
    input.select();
  }
  trigger.addEventListener('dblclick', event => {
    event.stopPropagation();
    openForm();
  });
  trigger.addEventListener('keydown', event => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      openForm();
    }
  });
  form.addEventListener('keydown', event => {
    if (event.key === 'Escape' && !saving) closeForm();
  });
  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (saving) return;
    const name = input.value.trim();
    if (!/^[A-Za-z][A-Za-z0-9_]{0,39}$/.test(name)) {
      status.textContent = '字母开头，可含英文字母、数字和下划线，最多40字符';
      return;
    }
    saving = true;
    input.disabled = true;
    status.textContent = '正在保存名称…';
    try {
      const state = await fetchState();
      const robotId = updateLabel(state);
      const id = `single-rename-${Date.now()}-${Math.random().toString(36).slice(2)}`;
      const response = await fetch('/dispatch-api/command', {
        method: 'POST',
        headers: {'Content-Type': 'application/json', 'X-OmniFleet-Token': state.token},
        body: JSON.stringify({op: 'robot_rename', id, name, robot_id: robotId, identity_revision: state.identity_revision}),
        signal: AbortSignal.timeout(5000),
      });
      if (!response.ok) throw new Error('更名请求未提交');
      const deadline = Date.now() + 5000;
      while (Date.now() < deadline) {
        const updated = await fetchState();
        const result = updated.commands?.[id];
        if (result) {
          if (result.phase !== 'renamed') throw new Error(result.message || '车载调度未接受更名');
          updateLabel(updated);
          status.textContent = '名称已更新';
          closeForm();
          return;
        }
        await new Promise(resolve => setTimeout(resolve, 250));
      }
      throw new Error('尚未收到更名结果，刷新后可查看最新名称');
    } catch (error) {
      status.textContent = error.message;
    } finally {
      saving = false;
      input.disabled = false;
    }
  });
})();

// G20 SLAM and saved map tools
async function requestOmnifleetSlamRestart(report) {
  async function state(path, options) {
    const response = await fetch('/single-slam/' + path, { cache: 'no-store', ...options });
    if (!response.ok) throw Error((await response.text()) || '车端重启接口不可用');
    return response.json();
  }
  let status = await state('restart', { method: 'POST' });
  const deadline = Date.now() + 160000;
  while (status.phase !== 'done' && status.phase !== 'failed') {
    report(status.message, false, 0);
    if (Date.now() >= deadline) throw Error('等待车端重启超时，请查看车端状态');
    await new Promise(resolve => setTimeout(resolve, 1200));
    status = await state('status');
  }
  if (status.phase === 'failed') throw Error(status.message);
  report(status.message);
}

function showOmnifleetSlamStatus(message, isError = false, timeout = 8500) {
  const id = 'omnifleet-slam-restart-status';
  let box = document.getElementById(id);
  if (!box) {
    box = document.createElement('div');
    box.id = id;
    box.setAttribute('role', 'status');
    box.style.cssText = 'position:fixed;bottom:18px;left:50%;transform:translateX(-50%);z-index:10000;max-width:80vw;padding:8px 12px;border-radius:6px;color:#fff;background:#253242;font:14px system-ui;pointer-events:none';
    document.body.append(box);
  }
  box.textContent = message;
  box.style.background = isError ? '#9d2525' : '#253242';
  clearTimeout(box.removeTimer);
  if (timeout > 0) box.removeTimer = setTimeout(() => box.remove(), timeout);
}

(() => {
  const bridge = new URL('/single-cloud-socket', location.href);
  bridge.protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
  const encoder = new TextEncoder();
  const decoder = new TextDecoder();

  function mapRequest(path) {
    const text = encoder.encode(path);
    const bytes = new Uint8Array(9 + text.length);
    bytes[1] = 1;
    new DataView(bytes.buffer).setUint32(4, text.length + 1, true);
    bytes.set(text, 8);
    return bytes;
  }

  function stackStringRequest(key, content = '') {
    // rcl_interfaces/SetParameters with one string parameter.
    const name = encoder.encode(key);
    const text = encoder.encode(content);
    const bytes = new Uint8Array(80 + name.length + text.length);
    const fields = new DataView(bytes.buffer);
    bytes[1] = 1;
    fields.setUint32(4, 1, true);
    fields.setUint32(8, name.length + 1, true);
    bytes.set(name, 12);
    const type = 13 + name.length;
    bytes[type] = 4;
    const value = 4 + Math.ceil((type + 2 - 4) / 8) * 8 + 16;
    fields.setUint32(value, text.length + 1, true);
    bytes.set(text, value + 4);
    const arrays = 4 + Math.ceil((value + text.length + 5 - 4) / 4) * 4;
    return bytes.subarray(0, arrays + 20); // Five empty array-valued fields.
  }

  function connect() {
    const socket = new WebSocket(bridge, ['foxglove.sdk.v1', 'foxglove.websocket.v1']);
    socket.binaryType = 'arraybuffer';
    const services = new Map();
    const pending = new Map();
    let nextId = 1;
    let changed = () => {};
    let statusChannel;
    let onLocalizationStatus;
    let watchingStatus = false;
    function subscribeStatus() {
      if (!onLocalizationStatus || statusChannel === undefined || watchingStatus || socket.readyState !== WebSocket.OPEN) return;
      socket.send(JSON.stringify({ op: 'subscribe', subscriptions: [{ id: 1, channelId: statusChannel }] }));
      watchingStatus = true;
    }
    socket.onmessage = ({ data }) => {
      if (typeof data === 'string') {
        const message = JSON.parse(data);
        if (message.op === 'advertiseServices') {
          for (const service of message.services) services.set(service.name, service.id);
          changed();
        } else if (message.op === 'advertise') {
          const channel = message.channels.find(item => item.topic === '/omnifleet_a2/waypoints/status' && item.encoding === 'cdr');
          if (channel) statusChannel = channel.id;
          subscribeStatus();
        } else if (message.op === 'serviceCallFailure') {
          pending.get(message.callId)?.reject(new Error(message.message || '车端服务调用失败'));
        }
        return;
      }
      const buffer = new DataView(data);
      if (watchingStatus && buffer.byteLength >= 22 && buffer.getUint8(0) === 1 && buffer.getUint32(1, true) === 1) {
        const length = buffer.getUint32(17, (buffer.getUint8(14) & 1) === 1);
        if (length > 0 && 21 + length <= buffer.byteLength) {
          onLocalizationStatus(decoder.decode(new Uint8Array(data, 21, length - 1)));
        }
        return;
      }
      if (buffer.byteLength < 13 || buffer.getUint8(0) !== 3) return;
      const request = pending.get(buffer.getUint32(5, true));
      if (!request || request.service !== buffer.getUint32(1, true)) return;
      try {
        const encodingLength = buffer.getUint32(9, true);
        const encoding = decoder.decode(new Uint8Array(data, 13, encodingLength));
        const cdr = 13 + encodingLength;
        if (encoding !== 'cdr' || cdr + 12 > buffer.byteLength) throw Error('服务响应格式无效');
        const little = (buffer.getUint8(cdr + 1) & 1) === 1;
        const result = cdr + (request.parameterResult ? 8 : 4);
        if (result + 8 > buffer.byteLength ||
            (request.parameterResult && buffer.getUint32(cdr + 4, little) !== 1)) throw Error('服务响应格式无效');
        const success = buffer.getUint8(result) === 1;
        const length = buffer.getUint32(result + 4, little);
        if (length < 1 || result + 8 + length > buffer.byteLength) throw Error('服务响应不完整');
        const message = decoder.decode(new Uint8Array(data, result + 8, length - 1));
        request.resolve({ success, message });
      } catch (error) {
        request.reject(error);
      }
    };
    socket.onclose = () => {
      for (const request of pending.values()) request.reject(Error('遥控 App 已断开车端连接'));
      changed();
    };
    async function callService(name, payload = Uint8Array.of(0, 1, 0, 0, 0), options = {}) {
      const label = options.label ?? '重启 SLAM 服务';
      if (!services.has(name)) {
        await new Promise((resolve, reject) => {
          const timer = setTimeout(() => {
            changed = () => {};
            reject(Error(`未收到车端${label}的公告`));
          }, options.discoveryTimeout ?? 6500);
          changed = () => {
            if (!services.has(name) && socket.readyState !== WebSocket.CLOSED) return;
            clearTimeout(timer);
            changed = () => {};
            if (services.has(name)) resolve();
            else reject(Error(`遥控 App 无法连接车端${label}`));
          };
          changed();
        });
      }
      if (socket.readyState !== WebSocket.OPEN) throw Error(`车端连接已断开，无法调用${label}`);
      const service = services.get(name);
      const id = nextId++;
      const encoding = encoder.encode('cdr');
      const request = new DataView(new ArrayBuffer(13 + encoding.length + payload.length));
      request.setUint8(0, 2);
      request.setUint32(1, service, true);
      request.setUint32(5, id, true);
      request.setUint32(9, encoding.length, true);
      new Uint8Array(request.buffer).set(encoding, 13);
      new Uint8Array(request.buffer).set(payload, 13 + encoding.length);
      try {
        return await new Promise((resolve, reject) => {
          const timer = setTimeout(() => reject(Error('车端响应超时，操作结果未确认')), options.timeout ?? 6500);
          pending.set(id, {
            service,
            parameterResult: options.parameterResult,
            resolve: (value) => { clearTimeout(timer); resolve(value); },
            reject: (error) => { clearTimeout(timer); reject(error); },
          });
          try { socket.send(request.buffer); }
          catch (error) { clearTimeout(timer); reject(error); }
        });
      } finally {
        pending.delete(id);
      }
    }
    return {
      callService,
      close: () => socket.close(),
      closed: () => socket.readyState >= WebSocket.CLOSING,
      watchLocalization(handler) {
        onLocalizationStatus = handler;
        subscribeStatus();
      },
    };
  }

  const dialog = document.createElement('dialog');
  dialog.style.cssText = 'max-width:min(82vw,380px);max-height:calc(100% - 12px);overflow:auto;width:320px;box-sizing:border-box;padding:12px 16px;border:0;color:inherit;font:14px/1.3 system-ui';
  dialog.innerHTML = '<form><h2 style="margin:0 0 8px;font-size:16px"></h2>'
    + '<ul aria-label="已保存地图" style="margin:0;padding:0;list-style:none;max-height:44vh;overflow:auto"></ul>'
    + '<label data-map-name>地图名称<input required maxlength="60" autocomplete="off"></label>'
    + '<div role="status" style="margin:6px 0;font-size:12px;overflow-wrap:anywhere"></div>'
    + '<div style="display:flex;justify-content:flex-end;gap:8px">'
    + '<button type="button">取消</button><button type="submit"></button></div></form>';
  const form = dialog.querySelector('form');
  const title = dialog.querySelector('h2');
  title.id = 'omnifleet-map-dialog-title';
  dialog.setAttribute('aria-labelledby', title.id);
  const mapList = dialog.querySelector('ul');
  const input = dialog.querySelector('input');
  const mapStatus = dialog.querySelector('[role="status"]');
  const cancel = dialog.querySelector('[type="button"]');
  const confirm = dialog.querySelector('[type="submit"]');
  input.style.cssText = 'display:block;box-sizing:border-box;width:100%;margin-top:4px;padding:5px 6px;font:inherit;color:inherit;background:#323338;border:1px solid #52535b;border-radius:4px';
  for (const action of [cancel, confirm]) {
    action.style.cssText = 'padding:5px 10px;color:inherit;background:#323338;border:1px solid #52535b;border-radius:4px;font:inherit';
  }
  let loadingMap = false;
  let mapDirectory = '';
  let dialogRevision = 0;
  let mapClient;
  let localizationClient;
  cancel.onclick = () => dialog.close();
  dialog.addEventListener('close', () => {
    if (dialog.open) return;
    mapClient?.close();
    mapClient = undefined;
  });

  function callMapService(service, payload, label, options = {}) {
    if (!mapClient || mapClient.closed()) mapClient = connect();
    return mapClient.callService(service, payload, { label, discoveryTimeout: 15000, ...options });
  }

  async function mapCatalog(key, path) {
    const deleting = key === '__delete_saved_map';
    const response = await fetch(deleting ? '/single-map-catalog/delete' : '/single-map-catalog', deleting ? {
      method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({path}),
    } : { cache: 'no-store' });
    if (!response.ok) throw Error((await response.text()) || '无法读取地图目录');
    return response.json();
  }

  function showLocalizationInstructions() {
    localizationClient?.close();
    const watcher = mapClient;
    localizationClient = watcher;
    mapClient = undefined;
    showOmnifleetSlamStatus('地图已加载。长按地图右上角的发布按钮，选「发布位姿估计」后再点一次发布按钮，然后从车的位置沿车头方向拖动。', false, 0);
    watcher?.watchLocalization(message => {
      if (localizationClient !== watcher) return;
      if (message.startsWith('正在用激光扫描精细对齐')) {
        showOmnifleetSlamStatus(message, false, 0);
      } else if (message.startsWith('初始定位未完成')) {
        showOmnifleetSlamStatus(message, true, 0);
      } else if (message.startsWith('重定位已确认')) {
        showOmnifleetSlamStatus(message);
        watcher.close();
        localizationClient = undefined;
      }
    });
  }

  function renderMapList(catalog) {
    mapList.replaceChildren();
    for (const map of catalog.maps) {
      const row = document.createElement('li');
      row.style.cssText = 'display:flex;align-items:center;gap:6px;padding:6px 0;border-bottom:1px solid #41424a';
      const name = document.createElement('span');
      name.style.cssText = 'min-width:0;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap';
      name.textContent = name.title = map.name;
      row.append(name);
      for (const [action, text] of [['load', '加载'], ['delete', '删除']]) {
        const control = document.createElement('button');
        control.type = 'button';
        control.style.cssText = cancel.style.cssText + ';white-space:nowrap';
        control.textContent = text;
        control.setAttribute('aria-label', text + ' ' + map.name);
        control.onclick = () => { void performMapAction(action, map.path, map.name); };
        row.append(control);
      }
      mapList.append(row);
    }
    mapStatus.textContent = catalog.maps.length ? catalog.directory : '车端暂无已保存地图';
  }

  async function openMapDialog(load) {
    if (!dialog.isConnected) document.body.append(dialog);
    const revision = ++dialogRevision;
    loadingMap = load;
    mapDirectory = '';
    dialog.className = tool.className;
    title.textContent = load ? '加载地图' : '保存地图';
    mapList.hidden = !load;
    input.parentElement.hidden = load;
    input.required = !load;
    input.value = '';
    cancel.textContent = load ? '关闭' : '取消';
    confirm.textContent = '保存';
    confirm.hidden = load;
    confirm.disabled = true;
    mapList.replaceChildren();
    mapStatus.textContent = '正在读取车端地图目录…';
    dialog.showModal();
    try {
      const catalog = await mapCatalog('__saved_maps', '');
      if (revision !== dialogRevision || !dialog.open) return;
      mapDirectory = catalog.directory;
      if (load) renderMapList(catalog);
      else mapStatus.textContent = mapDirectory;
      confirm.disabled = load || !mapDirectory;
    } catch (error) {
      if (revision === dialogRevision && dialog.open) mapStatus.textContent = error.message;
    }
  }

  async function performMapAction(operation, path, name) {
    if (cancel.disabled) return;
    const action = { load: '加载', save: '保存', delete: '删除' }[operation];
    confirm.disabled = cancel.disabled = true;
    mapList.inert = true;
    mapStatus.textContent = `正在${action}地图…`;
    try {
      if (operation === 'delete') {
        renderMapList(await mapCatalog('__delete_saved_map', path));
        showOmnifleetSlamStatus(`已删除 ${name}，源文件已移入回收目录`);
      } else {
        const result = await callMapService(`/omnifleet_t2/waypoints/map_${operation}`, mapRequest(path), `${action}地图服务`, { timeout: operation === 'load' ? 85000 : 65000 });
        if (!result.success) throw Error(result.message || `车端未确认${action}地图`);
        dialog.close();
        if (operation === 'load' && result.message.includes('请使用初始定位工具')) showLocalizationInstructions();
        else showOmnifleetSlamStatus(operation === 'load' ? '地图和关联航点已加载' : `地图和航点已保存至 ${path}`);
      }
    } catch (error) {
      mapStatus.textContent = error.message;
    } finally {
      cancel.disabled = false;
      confirm.disabled = loadingMap || !mapDirectory;
      mapList.inert = false;
    }
  }

  form.onsubmit = (event) => {
    event.preventDefault();
    if (confirm.disabled || loadingMap) return;
    const name = input.value.trim().replace(/[/\\]/g, '-');
    const stamp = new Date().toISOString().replace(/[^0-9]/g, '');
    if (!name) { mapStatus.textContent = '请输入地图名称'; return; }
    void performMapAction('save', `${mapDirectory}/${name}-${stamp}`, name);
  };
  dialog.addEventListener('cancel', (event) => { if (cancel.disabled) event.preventDefault(); });

  const tool = document.createElement('div');
  tool.style.cssText = 'position:absolute;top:10px;left:10px;z-index:1;display:flex;flex-direction:column';
  const button = document.createElement('button');
  button.id = 'omnifleet-app-slam-restart-button';
  button.type = 'button';
  button.title = '清空当前 SLAM 地图并重新建图';
  button.setAttribute('aria-label', button.title);
  button.style.cssText = 'box-sizing:border-box;width:36px;height:36px;display:flex;flex-direction:column;justify-content:center;gap:1px;padding:0';
  const icon = document.createElement('span');
  icon.textContent = '↻';
  icon.style.cssText = 'font:21px/18px system-ui';
  icon.setAttribute('aria-hidden', 'true');
  const label = document.createElement('span');
  label.textContent = 'SLAM';
  label.style.cssText = 'font:bold 8px/9px system-ui';
  label.setAttribute('aria-hidden', 'true');
  button.append(icon, label);
  tool.append(button);
  button.addEventListener('pointerdown', event => event.stopPropagation());
  for (const [name, paths, load] of [
    ['加载地图', ['M3 19V5h6l2 3h9v4', 'M3 19l3-8h16l-3 8z'], true],
    ['保存地图', ['M5 3h12l4 4v14H3V3z', 'M7 3v6h10V3', 'M7 21v-8h10v8'], false],
  ]) {
    const mapButton = document.createElement('button');
    mapButton.type = 'button';
    mapButton.title = name;
    mapButton.setAttribute('aria-label', name);
    mapButton.style.cssText = button.style.cssText;
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    for (const [key, value] of Object.entries({ viewBox: '0 0 24 24', width: '19', height: '19', fill: 'none', stroke: 'currentColor', 'stroke-width': '1.6', 'stroke-linejoin': 'round', 'stroke-linecap': 'round', 'aria-hidden': 'true' })) svg.setAttribute(key, value);
    for (const d of paths) {
      const path = document.createElementNS(svg.namespaceURI, 'path');
      path.setAttribute('d', d);
      svg.append(path);
    }
    const caption = label.cloneNode(false);
    caption.textContent = load ? '加载' : '保存';
    mapButton.append(svg, caption);
    mapButton.addEventListener('pointerdown', event => event.stopPropagation());
    mapButton.onclick = (event) => { event.stopPropagation(); void openMapDialog(load); };
    tool.append(mapButton);
  }
  let active = false;
  button.onclick = async (event) => {
    event.stopPropagation();
    if (active) return;
    active = true;
    button.disabled = true;
    button.setAttribute('aria-busy', 'true');
    icon.textContent = '…';
    try {
      await requestOmnifleetSlamRestart(showOmnifleetSlamStatus);
      localizationClient?.close();
      localizationClient = undefined;
    } catch (error) {
      showOmnifleetSlamStatus(error.message || String(error), true);
    } finally {
      active = false;
      button.disabled = false;
      button.removeAttribute('aria-busy');
      icon.textContent = '↻';
    }
  };
  function mount() {
    if (tool.isConnected) return;
    const measure = document.querySelector('[data-testid="measure-button"]');
    let scene = measure?.parentElement;
    // The renderer's canvas and its side toolbar share a positioned scene root.
    while (scene && !scene.querySelector(':scope > canvas')) scene = scene.parentElement;
    if (!scene || !measure) return;
    tool.className = measure.closest('.MuiPaper-root')?.className ?? '';
    for (const control of tool.children) control.className = measure.className;
    scene.append(tool);
  }
  const observeScene = () => {
    mount();
    new MutationObserver(mount).observe(document.body, { childList: true, subtree: true });
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', observeScene, { once: true });
  else observeScene();
})();
