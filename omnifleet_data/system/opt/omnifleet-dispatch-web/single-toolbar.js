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
