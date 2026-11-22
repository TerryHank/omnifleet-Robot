const {JSDOM, VirtualConsole} = require('/home/iecme/omnifleet_ws/src/visualization/foxglove_studio_source/node_modules/jsdom');
const assert = require('assert');

const dom = new JSDOM('<div><div id="panel"></div></div>', {virtualConsole:new VirtualConsole()});
global.document = dom.window.document;
global.window = dom.window;
global.CustomEvent = dom.window.CustomEvent;
dom.window.HTMLElement.prototype.scrollIntoView = function() { this.dataset.scrolled = 'true'; };

(async () => {
  const {initNav2HotParamsPanel} = await import('./Nav2PermanentPanel.test.mjs');
  const context = {
    panelElement: document.querySelector('#panel'),
    initialState: {},
    saveState: () => {},
    watch: () => {},
    subscribe: () => {},
    callService: async () => ({
      success:true,
      message:JSON.stringify({saved:{},algorithms:{global:{current:'smac_2d'},local:{current:'hot_dwb'}},parameter_links:{}}),
    }),
  };
  const dispose = initNav2HotParamsPanel(context);
  await new Promise(resolve => setTimeout(resolve, 650));
  const search = document.querySelector('[data-testid="nav2-parameter-search"]');
  const results = document.querySelector('[data-testid="nav2-parameter-search-results"]');
  const query = value => {
    search.value = value;
    search.dispatchEvent(new dom.window.Event('input', {bubbles:true}));
    return [...results.querySelectorAll('button')];
  };

  let matches = query('膨胀');
  assert(matches.some(button => button.dataset.parameterId === 'costmap_radius'));
  assert(matches.some(button => button.dataset.parameterId === 'costmap_scaling'));
  matches.find(button => button.dataset.parameterId === 'costmap_radius').click();
  assert.equal(document.activeElement.dataset.testid, 'nav2-input-costmap_radius');
  assert.equal(document.activeElement.dataset.scrolled, 'true');
  assert(document.activeElement.closest('details').open);

  matches = query('yaw_goal_tolerance');
  assert.equal(matches[0].dataset.parameterId, 'goal_yaw_tolerance');
  search.dispatchEvent(new dom.window.KeyboardEvent('keydown', {key:'Enter', bubbles:true}));
  assert.equal(document.activeElement.dataset.testid, 'nav2-input-goal_yaw_tolerance');

  matches = query('rotate_to_heading_min_angle');
  assert.equal(matches[0].dataset.parameterId, 'rpp_rotate_to_heading_min_angle');
  matches[0].click();
  assert.equal(document.activeElement.dataset.testid, 'nav2-local-algorithm');
  assert.equal(document.activeElement.value, 'hot_dwb');
  assert(document.querySelector('[data-testid="nav2-save-status"]').textContent.includes('请先在已定位的下拉框切换算法'));

  query('不存在的关键词');
  assert(results.textContent.includes('没有匹配参数'));
  dispose();
  console.log('PASS: Chinese/English search, Enter/click locate, section reveal, inactive-algorithm guidance');
})().catch(error => { console.error(error); process.exitCode = 1; });
