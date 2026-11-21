(() => {
  const endpoint = '/dispatch-api/bags';
  const trigger = document.querySelector('[data-bag-open]');
  if (!trigger) return;
  trigger.setAttribute('aria-haspopup', 'dialog');
  trigger.setAttribute('aria-controls', 'bag-dialog');
  document.body.insertAdjacentHTML('beforeend', `
    <dialog id="bag-dialog" aria-labelledby="bag-dialog-title">
      <header>
        <h2 id="bag-dialog-title">本机 Bag</h2>
        <button type="button" id="bag-close" aria-label="关闭">关闭</button>
      </header>
      <div class="bag-controls">
        <button type="button" id="bag-start" class="bag-primary" disabled>开始录制</button>
        <button type="button" id="bag-stop" disabled>停止录制</button>
        <p id="bag-state" role="status">读取录制状态…</p>
      </div>
      <p id="bag-feedback" role="status"></p>
      <div class="bag-table">
        <table aria-label="已完成的 Bag">
          <thead><tr><th>Bag 名称</th><th>时间</th><th>大小</th><th>操作</th></tr></thead>
          <tbody id="bag-list"></tbody>
        </table>
        <p id="bag-empty" hidden>暂无已完成的 Bag。</p>
      </div>
    </dialog>`);

  const byId = id => document.getElementById(id);
  const dialog = byId('bag-dialog');
  const state = byId('bag-state');
  const feedback = byId('bag-feedback');
  const start = byId('bag-start');
  const stop = byId('bag-stop');
  const list = byId('bag-list');
  const dateFormat = new Intl.DateTimeFormat('zh-CN', {dateStyle: 'short', timeStyle: 'medium'});
  let active;
  let known = false;
  let pending = false;
  let refreshing = false;
  let previousRecords = '';

  function updateButtons() {
    start.disabled = pending || !known || !!active;
    stop.disabled = pending || !known || !active;
    list.querySelectorAll('button').forEach(button => { button.disabled = pending || !known; });
  }

  function sizeLabel(size) {
    if (size < 1024) return `${size} B`;
    if (size < 1024 ** 2) return `${(size / 1024).toFixed(1)} KB`;
    if (size < 1024 ** 3) return `${(size / 1024 ** 2).toFixed(1)} MB`;
    return `${(size / 1024 ** 3).toFixed(2)} GB`;
  }

  function render(records) {
    const key = JSON.stringify(records);
    if (key === previousRecords) return;
    previousRecords = key;
    list.replaceChildren();
    byId('bag-empty').hidden = records.length > 0;
    for (const record of records) {
      const row = list.insertRow();
      row.insertCell().textContent = record.name;
      row.insertCell().textContent = dateFormat.format(record.date * 1000);
      row.insertCell().textContent = sizeLabel(record.size);
      const remove = document.createElement('button');
      remove.type = 'button';
      remove.className = 'bag-delete';
      remove.textContent = '删除';
      remove.setAttribute('aria-label', `删除 ${record.name}`);
      remove.onclick = () => {
        if (window.confirm(`删除 Bag「${record.name}」？此操作无法撤销。`)) {
          void change(`${endpoint}/${encodeURIComponent(record.name)}`, 'DELETE');
        }
      };
      row.insertCell().append(remove);
    }
  }

  async function request(url, method) {
    const signal = AbortSignal.timeout(method === 'GET' ? 5000 : 35000);
    const response = await fetch(url, {method, cache: 'no-store', signal});
    if (!response.ok) throw new Error((await response.text()) || `HTTP ${response.status}`);
    return response.json();
  }

  async function refresh() {
    if (refreshing) return;
    refreshing = true;
    try {
      const snapshot = await request(endpoint, 'GET');
      active = snapshot.active;
      known = true;
      state.textContent = active ? `录制中 · ${active}` : '未录制';
      render(snapshot.bags);
    } catch (error) {
      known = false;
      state.textContent = `读取录制状态失败 · ${error.message}`;
    } finally {
      refreshing = false;
      updateButtons();
    }
  }

  async function change(url, method) {
    if (pending) return;
    pending = true;
    updateButtons();
    feedback.textContent = method === 'DELETE' ? '正在删除…' : '正在处理…';
    try {
      feedback.textContent = (await request(url, method)).message;
    } catch (error) {
      feedback.textContent = error.message;
    } finally {
      await refresh();
      pending = false;
      updateButtons();
    }
  }

  trigger.addEventListener('click', () => {
    dialog.showModal();
    void refresh();
  });
  byId('bag-close').onclick = () => dialog.close();
  start.onclick = () => void change(`${endpoint}/start`, 'POST');
  stop.onclick = () => void change(`${endpoint}/stop`, 'POST');
  setInterval(() => {
    if (dialog.open && !document.hidden && !pending) void refresh();
  }, 1800);
})();
