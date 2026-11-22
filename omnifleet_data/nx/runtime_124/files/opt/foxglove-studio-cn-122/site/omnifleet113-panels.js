(function(){
let maxSteeringDegrees = 60;
const driveSpeedKey = "omnifleet.robot124.driveSpeed";
const clampDriveSpeed = value => Math.max(0.3, Math.min(1.0, value));
const savedDriveSpeed = Number(localStorage.getItem(driveSpeedKey));
let driveSpeed = savedDriveSpeed > 0 ? clampDriveSpeed(savedDriveSpeed) : 0.3;
async function refreshSteeringLimit() {
  try {
    const response = await fetch("/api/steering-limit", {cache:"no-store"});
    if (!response.ok) return;
    const result = await response.json();
    if (Number.isInteger(result.max_angle_deg)) maxSteeringDegrees = result.max_angle_deg;
  } catch {}
}
void refreshSteeringLimit();
window.addEventListener("focus", refreshSteeringLimit);
function initAckermannDrive(context) {
  const root = context.panelElement;
  const wheelbase = 0.22492;
  const directions = [
    ["右转向", 0, -1], ["右后", -1, -1], ["后退", -1, 0], ["左后", -1, 1],
    ["左转向", 0, 1], ["左前", 1, 1], ["前进", 1, 0], ["右前", 1, -1],
  ];
  const idleText = "拖动摇杆，松手停止";
  root.className = "a2-drive";
  root.innerHTML = `<style>
    .a2-drive {
      --drive-accent:#9480ed;
      --drive-danger:#f54966;
      --drive-border:color-mix(in srgb,currentColor 19%,transparent);
      --drive-surface:color-mix(in srgb,currentColor 7%,transparent);
      --drive-muted:color-mix(in srgb,currentColor 70%,transparent);
      height:100%; overflow:auto; box-sizing:border-box; padding:12px;
      font:13px Roboto,"Microsoft YaHei UI",sans-serif;
    }
    .a2-drive-console { display:grid; gap:12px; width:min(100%,260px); margin-inline:auto; }
    .a2-drive-speed {
      display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center;
      gap:6px; padding:6px 8px 6px 11px; border:1px solid var(--drive-border); border-radius:6px;
    }
    .a2-drive-speed > span:last-child { display:flex; gap:7px; align-items:center; color:var(--drive-muted); font-size:12px; }
    .a2-drive input {
      box-sizing:border-box; width:5em; min-height:28px; padding:3px 6px;
      color:inherit; background:var(--drive-surface); border:1px solid var(--drive-border);
      border-radius:4px; font:inherit; font-variant-numeric:tabular-nums;
    }
    .a2-drive-stick {
      position:relative; box-sizing:border-box; width:min(100%,210px); aspect-ratio:1; margin-inline:auto;
      border:1px solid var(--drive-border); border-radius:50%; background:var(--drive-surface);
      touch-action:none; cursor:grab; user-select:none;
    }
    .a2-drive-stick[data-held] { cursor:grabbing; border-color:var(--drive-accent); }
    .a2-drive-stick::before {
      content:""; position:absolute; inset:19%; border:1px solid var(--drive-border); border-radius:50%;
      background:linear-gradient(var(--drive-border),var(--drive-border)) center / 1px 100% no-repeat,
        linear-gradient(var(--drive-border),var(--drive-border)) center / 100% 1px no-repeat;
    }
    .a2-drive-knob {
      position:absolute; left:50%; top:50%; width:35%; aspect-ratio:1; border-radius:50%;
      display:grid; place-items:center; color:#15151a; background:var(--drive-accent);
      box-shadow:0 2px 8px #0005; pointer-events:none;
      transform:translate(calc(-50% + var(--stick-x,0px)),calc(-50% + var(--stick-y,0px)));
    }
    .a2-drive-knob::after {
      content:""; width:24%; aspect-ratio:1; border:1px solid currentColor; border-radius:50%; opacity:.7;
    }
    .a2-drive-stick span[aria-hidden] { position:absolute; color:var(--drive-muted); line-height:1; pointer-events:none; }
    .a2-drive-stick .up { top:8%; left:50%; transform:translateX(-50%); }
    .a2-drive-stick .down { bottom:8%; left:50%; transform:translateX(-50%); }
    .a2-drive-stick .left { left:8%; top:50%; transform:translateY(-50%); }
    .a2-drive-stick .right { right:8%; top:50%; transform:translateY(-50%); }
    .a2-drive p { margin:0; min-height:1.5em; color:var(--drive-muted); text-align:center; font-size:12px; line-height:1.5; }
    .a2-drive [data-stop] {
      display:flex; justify-content:center; align-items:center; gap:7px; min-height:36px; border-radius:6px;
      color:inherit; font:inherit; font-weight:600; background:var(--drive-surface);
      border:1px solid var(--drive-border); cursor:pointer;
    }
    .a2-drive [data-stop]::before { content:""; width:9px; height:9px; border-radius:1px; background:var(--drive-danger); }
    .a2-drive [data-stop]:hover { border-color:var(--drive-danger); }
    .a2-drive :is(.a2-drive-stick,input,button):focus-visible { outline:2px solid var(--drive-accent); outline-offset:2px; }
  </style>
  <div class="a2-drive-console">
    <div class="a2-drive-stick" role="group" tabindex="0" aria-label="摇杆方向控制"
        aria-keyshortcuts="ArrowUp ArrowDown ArrowLeft ArrowRight">
      <span class="up" aria-hidden="true">↑</span><span class="down" aria-hidden="true">↓</span>
      <span class="left" aria-hidden="true">←</span><span class="right" aria-hidden="true">→</span>
      <div class="a2-drive-knob" aria-hidden="true"></div>
    </div>
    <p role="status">${idleText}</p>
    <button type="button" data-stop>停止</button>
  </div>`;
  const stick = root.querySelector(".a2-drive-stick");
  const status = root.querySelector(".a2-drive-stick + p");
  const keys = new Set();
  const arrowKeys = ["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"];
  let pointerId;
  let held;
  let timer;
  const stream = Date.now().toString(36) + "-" + Math.random().toString(36).slice(2);
  let sequence = 0;
  let inflight = 0;

  async function send(linear, angular) {
    const stopping = linear === 0 && angular === 0;
    if (!stopping && inflight >= 4) return;
    const frame = ++sequence;
    inflight += 1;
    try {
      const response = await fetch("/api/drive", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ linear, angular_z: angular, stream, sequence: frame }),
        keepalive: stopping,
        signal: AbortSignal.timeout(stopping ? 1000 : 320),
      });
      if (!response.ok) throw new Error("Drive request failed");
      if (!stopping && held && frame === sequence) status.textContent = held.label;
    } catch {
      if (!stopping && held && frame === sequence) status.textContent = "控制链路延迟";
    } finally {
      inflight -= 1;
    }
  }

  function stop() {
    held = undefined;
    clearInterval(timer);
    timer = undefined;
    status.textContent = idleText;
    void send(0, 0);
  }

  function tick() {
    if (!held) return;
    const { travel, steering, speed } = held;
    const linear = travel * speed;
    // The front-wheel steering sign is left-positive. Reverse travel reverses body yaw.
    const angular = travel ? linear * Math.tan(steering * maxSteeringDegrees * Math.PI / 180) / wheelbase : steering;
    void send(linear, angular);
  }

  function updateStick(x, y) {
    const magnitude = Math.hypot(x, y);
    const radius = stick.clientWidth * 0.29;
    const scale = radius / Math.max(1, magnitude);
    stick.style.setProperty("--stick-x", `${x * scale}px`);
    stick.style.setProperty("--stick-y", `${y * scale}px`);

    if (magnitude < 0.16) {
      if (held) stop();
      return;
    }
    const sector = (Math.round(Math.atan2(y, x) / (Math.PI / 4)) + 8) % 8;
    const changedDirection = held?.sector !== sector;
    const [label, travel, turn] = directions[sector];
    const steering = travel && turn ? turn * Math.abs(x) / Math.max(1, magnitude) : turn;
    held = {
      sector, label, travel, steering,
      speed: driveSpeed,
    };
    if (changedDirection) {
      status.textContent = label;
      tick();
    }
    timer ??= setInterval(tick, 80);
  }

  function endGesture() {
    const captured = pointerId;
    pointerId = undefined;
    if (captured !== undefined && stick.hasPointerCapture(captured)) stick.releasePointerCapture(captured);
    keys.clear();
    stick.removeAttribute("data-held");
    updateStick(0, 0);
  }

  function updatePointer(event) {
    const { left, top, width, height } = stick.getBoundingClientRect();
    updateStick((event.clientX - left - width / 2) / (width / 2),
                (event.clientY - top - height / 2) / (height / 2));
  }

  stick.addEventListener("pointerdown", event => {
    if (event.button !== 0 || pointerId !== undefined || keys.size) return;
    pointerId = event.pointerId;
    stick.setPointerCapture(pointerId);
    stick.setAttribute("data-held", "");
    updatePointer(event);
  });
  stick.addEventListener("pointermove", event => {
    if (event.pointerId === pointerId) updatePointer(event);
  });
  for (const type of ["pointerup", "pointercancel", "lostpointercapture"]) {
    stick.addEventListener(type, event => {
      if (event.pointerId === pointerId) endGesture();
    });
  }

  function updateKeyboard() {
    stick.toggleAttribute("data-held", keys.size > 0);
    updateStick(Number(keys.has("ArrowRight")) - Number(keys.has("ArrowLeft")),
                Number(keys.has("ArrowDown")) - Number(keys.has("ArrowUp")));
  }
  stick.addEventListener("keydown", event => {
    if (!arrowKeys.includes(event.key)) return;
    event.preventDefault();
    if (pointerId !== undefined || event.repeat) return;
    keys.add(event.key);
    updateKeyboard();
  });
  stick.addEventListener("keyup", event => {
    if (!keys.delete(event.key)) return;
    event.preventDefault();
    updateKeyboard();
  });
  stick.addEventListener("blur", endGesture);
  root.querySelector("[data-stop]").addEventListener("click", () => {
    const wasHeld = Boolean(held);
    endGesture();
    if (!wasHeld) stop();
  });

  context.onRender = (_state, done) => done();
  const onVisibility = () => { if (document.hidden) endGesture(); };
  window.addEventListener("blur", endGesture);
  window.addEventListener("pagehide", endGesture);
  document.addEventListener("visibilitychange", onVisibility);
  return () => {
    endGesture();
    window.removeEventListener("blur", endGesture);
    window.removeEventListener("pagehide", endGesture);
    document.removeEventListener("visibilitychange", onVisibility);
  };
}


function initEncoderSpeed(context) {
  const root = context.panelElement;
  root.style.cssText = "height:100%;overflow:hidden;background:#15151b;color:#dddde3;position:relative";
  root.innerHTML = '<canvas style="width:100%;height:100%;display:block" aria-label="编码器反馈车速弧形仪表"></canvas>';
  const canvas = root.querySelector("canvas");
  const ctx = canvas.getContext("2d");
  const topic = "/omnifleet_a2/chassis/velocity_raw";
  let speed, lastAt = 0;
  function draw() {
    const rect = root.getBoundingClientRect();
    if (!rect.width || !rect.height) return;
    const ratio = window.devicePixelRatio || 1;
    canvas.width = Math.round(rect.width * ratio);
    canvas.height = Math.round(rect.height * ratio);
    ctx.setTransform(ratio,0,0,ratio,0,0);
    const width=rect.width, height=rect.height;
    const radius=Math.max(20,Math.min(width*0.36,height*0.44));
    const cx=width/2, cy=height*0.60;
    const start=Math.PI*5/6, sweep=Math.PI*4/3;
    const fresh=Number.isFinite(speed) && performance.now()-lastAt < 3000;
    const gradient=ctx.createLinearGradient(cx-radius,0,cx+radius,0);
    gradient.addColorStop(0,"#2196f3");gradient.addColorStop(1,"#ff9800");
    ctx.lineWidth=Math.max(10,radius*.12);
    ctx.lineCap="butt";
    ctx.beginPath();ctx.arc(cx,cy,radius,start,start+sweep);
    ctx.strokeStyle=gradient;ctx.globalAlpha=.42;ctx.stroke();ctx.globalAlpha=1;
    if (fresh) {
      const angle=start+((Math.max(-1,Math.min(1,speed))+1)/2)*sweep;
      ctx.strokeStyle="#e8e2ff";ctx.lineWidth=Math.max(2,radius*.018);
      ctx.beginPath();ctx.moveTo(cx+Math.cos(angle)*radius*.88,cy+Math.sin(angle)*radius*.88);
      ctx.lineTo(cx+Math.cos(angle)*radius*1.09,cy+Math.sin(angle)*radius*1.09);ctx.stroke();
    }
    ctx.textAlign="center";ctx.textBaseline="middle";
    ctx.fillStyle="#a5a5b4";ctx.font=Math.max(11,Math.min(16,radius*.10))+'px Roboto,"Microsoft YaHei UI",sans-serif';
    ctx.fillText("编码器反馈车速",cx,cy-radius*.43);
    ctx.fillStyle="#f0edf7";ctx.font='600 '+Math.max(23,Math.min(56,radius*.32))+'px Roboto,sans-serif';
    ctx.fillText(fresh?speed.toFixed(3):"—",cx,cy-radius*.12);
    ctx.fillStyle="#b7b4c3";ctx.font=Math.max(12,radius*.12)+'px Roboto,sans-serif';
    ctx.fillText("m/s",cx,cy+radius*.14);
    ctx.font=Math.max(11,radius*.09)+'px Roboto,"Microsoft YaHei UI",sans-serif';
    ctx.fillText(fresh?(Math.abs(speed)<.0005?"静止":speed>0?"前进":"倒车"):"等待编码器反馈",cx,cy+radius*.36);
    for (const [fraction,label] of [[0,"−1"],[.5,"0"],[1,"+1"]]) {
      const angle=start+fraction*sweep;
      ctx.fillText(label,cx+Math.cos(angle)*radius*1.23,cy+Math.sin(angle)*radius*1.23);
    }
    canvas.setAttribute("aria-label","编码器反馈车速 "+(fresh?speed.toFixed(3)+" m/s":"等待反馈"));
  }
  context.subscribe([{topic}]);context.watch("currentFrame");
  context.onRender=(state,done)=>{
    for(const event of state.currentFrame || []) {
      const value=event.topic===topic?event.message?.linear?.x:undefined;
      if(Number.isFinite(value)){speed=value;lastAt=performance.now();}
    }
    draw();done();
  };
  const resize=new ResizeObserver(draw);resize.observe(root);
  const expiry=setInterval(draw,500);
  return ()=>{resize.disconnect();clearInterval(expiry);};
}

function initDriveSpeed(context) {
  const root = context.panelElement;
  root.innerHTML = `<style>
    .a2-drive-speed {display:flex;align-items:center;gap:8px;padding:10px 12px;
      font:13px Roboto,"Microsoft YaHei UI",sans-serif}
    .a2-drive-speed input {flex:1;min-width:70px;accent-color:#9480ed;cursor:pointer;color:inherit;
      font:inherit;background:#a7a6af16;border:1px solid #a7a6af55;border-radius:4px}
  </style>
  <label class="a2-drive-speed">
    <input type="range" min="0.3" max="1.0" step="0.01" aria-label="行驶速度">
    <output data-drive-speed></output>
  </label>`;
  const input = root.querySelector("input");
  const value = root.querySelector('[data-drive-speed]');
  input.value = driveSpeed;
  const renderSpeed = () => { value.textContent = driveSpeed.toFixed(2) + " m/s"; };
  renderSpeed();
  input.addEventListener("input", () => {
    driveSpeed = clampDriveSpeed(input.valueAsNumber);
    renderSpeed();
    localStorage.setItem(driveSpeedKey, String(driveSpeed));
  });
}

function initSteeringCenter(context) {
  return initSteeringSetting(context, false);
}

function initSteeringLimit(context) {
  return initSteeringSetting(context, true);
}

function initSteeringSetting(context, isLimit) {
  const root = context.panelElement;
  root.style.overflow = "auto";
  const label = isLimit ? "最大转向角度" : "零点偏置";
  root.innerHTML = `<style>
    .a2-steering-setting {display:grid;grid-template-columns:1fr auto;gap:8px;
      margin:8px 12px;padding-top:10px;border-top:1px solid #a7a6af40;
      font:13px Roboto,"Microsoft YaHei UI",sans-serif}
    .a2-steering-setting label {display:flex;justify-content:space-between;gap:8px;grid-column:1/-1}
    .a2-steering-setting input[type=range] {width:100%;min-width:70px;accent-color:#9480ed;cursor:pointer}
    .a2-steering-setting button {color:inherit;font:inherit;background:#a7a6af16;
      border:1px solid #a7a6af65;border-radius:4px;padding:4px 9px;cursor:pointer}
    .a2-steering-setting input:disabled,.a2-steering-setting button:disabled {opacity:.5}
    .a2-steering-setting output {grid-column:1/-1;font-size:12px;min-height:16px}
    .a2-steering-setting span {font-variant-numeric:tabular-nums;white-space:nowrap}
  </style>
  <form class="a2-steering-setting">
    <label for="${isLimit ? "a2-steering-limit" : "a2-center-offset"}">当前值 <span data-value>—</span></label>
    <input id="${isLimit ? "a2-steering-limit" : "a2-center-offset"}" type="range" min="${isLimit ? 0 : -90}" max="${isLimit ? 60 : 90}" step="1"
      aria-label="${label}" disabled>
    <button type="submit" disabled>保存</button>
    <output role="status"></output>
  </form>`;
  const form = root.querySelector(".a2-steering-setting");
  const endpoint = isLimit ? "/api/steering-limit" : "/api/steering-center";
  const field = isLimit ? "max_angle_deg" : "offset_deg";
  const input = form.querySelector("input");
  const button = form.querySelector("button");
  const number = form.querySelector("[data-value]");
  const status = form.querySelector("output");
  function showValue() {
    number.textContent = (isLimit ? "±" : "") + input.value + "°";
  }
  async function sync(selected) {
    input.disabled = button.disabled = true;
    status.textContent = selected === undefined ? "读取中…" : "保存中…";
    try {
      const options = selected === undefined ? {} : {
        method:"POST", headers:{"Content-Type":"application/json"},
        body:JSON.stringify({[field]:selected})
      };
      const response = await fetch(endpoint, {...options,cache:"no-store"});
      if (!response.ok) throw new Error("Setting request failed");
      const result = await response.json();
      if (!Number.isInteger(result[field])) throw new Error("Invalid setting");
      input.value = result[field];
      showValue();
      if (isLimit) maxSteeringDegrees = result[field];
      status.textContent = selected === undefined ? "" : "已保存";
    } catch {
      status.textContent = selected === undefined ? "读取失败，请重试" : "保存未确认，请重试";
    } finally {
      input.disabled = button.disabled = false;
    }
  }
  input.addEventListener("input", showValue);
  input.addEventListener("change", () => void sync(input.valueAsNumber));
  form.addEventListener("submit", event => {
    event.preventDefault();
    void sync(input.valueAsNumber);
  });
  void sync();
}

function initBatteryVoltage(context) {
  const root = context.panelElement;
  root.style.overflow = "auto";
  root.innerHTML = `<style>
    .a2-voltage {font:600 32px/1.15 Roboto,"Microsoft YaHei UI",sans-serif;
      padding:5px 12px;font-variant-numeric:tabular-nums}
  </style><div class="a2-voltage" data-testid="robot124-battery-voltage">等待电压数据…</div>`;
  const value = root.querySelector(".a2-voltage");
  context.subscribe([{ topic: "/omnifleet_a2/chassis/voltage" }]);
  context.watch("currentFrame");
  context.onRender = (state, done) => {
    const message = state.currentFrame?.at(-1)?.message;
    if (Number.isFinite(message?.data)) value.textContent = message.data.toFixed(1) + " V";
    done();
  };
}

function initNav2Builtin(context) {
  const root = context.panelElement;
  const host = root.parentElement;
  const oldPosition = host.style.position;
  host.style.position = 'relative';
  root.className = 'omnifleet-nav2-hot-params';
  root.style.overflowY = 'auto';
  root.innerHTML = `<style>

  .omnifleet-nav2-hot-params {
    --panel-bg: #f2f3f8;
    --surface: #fff;
    --field: #f9f9fb;
    --hover: #edecf3;
    --line: #d6d9e5;
    --text: #24242a;
    --muted: #5e5c69;
    --accent: #6247c6;
    --selected: #ebe5ff;
    --success: #14643f;
    --danger: #a61b38;
    --warning: #805000;
    color-scheme: light;
    position: absolute;
    inset: 0;
    min-height: 0;
    overflow-wrap: anywhere;
    scrollbar-gutter: stable;
    scrollbar-color: var(--line) var(--panel-bg);
    container: parameter-panel / inline-size;
    padding: 0 10px 20px;
    background: var(--panel-bg);
    color: var(--text);
    font: calc(12px * var(--panel-font-scale, 1))/1.45 "Inter", system-ui, sans-serif;
  }

  html[data-color-mode="dark"] .omnifleet-nav2-hot-params {
    --panel-bg: #191a21;
    --surface: #24252f;
    --field: #1e1f28;
    --hover: #333239;
    --line: #3d3b47;
    --text: #e1e1e4;
    --muted: #adaab9;
    --accent: #b29eff;
    --selected: #352a53;
    --success: #77d6ab;
    --danger: #ff9baa;
    --warning: #e9bc76;
    color-scheme: dark;
  }

  .omnifleet-nav2-hot-params, .omnifleet-nav2-hot-params * { box-sizing: border-box; }
  .omnifleet-nav2-hot-params [hidden] { display: none !important; }
  .omnifleet-nav2-hot-params :is(.hint, small) { color: var(--muted); font-size: .86em; }
  .omnifleet-nav2-hot-params small { display: block; }
  .omnifleet-nav2-hot-params .hint { margin: 5px 0; }
  .omnifleet-nav2-hot-params a { color: var(--accent); cursor: pointer; text-underline-offset: 3px; }
  .omnifleet-nav2-hot-params h4 { font-size: .95em; margin: 12px 0 5px; }
  .omnifleet-nav2-hot-params :is(button, input, select) {
    min-width: 0;
    color: var(--text);
    font: inherit;
    border: 1px solid var(--line);
    border-radius: 6px;
  }
  .omnifleet-nav2-hot-params :is(input, select) {
    width: 100%;
    padding: 4px 6px;
    background: var(--field);
    font-variant-numeric: tabular-nums;
  }
  .omnifleet-nav2-hot-params button {
    padding: 4px 7px;
    background: var(--surface);
    cursor: pointer;
  }
  .omnifleet-nav2-hot-params :is(button, input, select):disabled { opacity: .48; cursor: not-allowed; }
  .omnifleet-nav2-hot-params button:not(:disabled):hover { background: var(--hover); }
  .omnifleet-nav2-hot-params :is(button, a, input, select, summary):focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: -2px;
  }
  .omnifleet-nav2-hot-params input[aria-invalid="true"] { border-color: var(--danger); }
  .omnifleet-nav2-hot-params input[type="checkbox"] {
    accent-color: var(--accent);
    justify-self: end;
    width: 16px;
    height: 16px;
    cursor: pointer;
  }
  .omnifleet-nav2-hot-params button[aria-pressed="true"],
  .omnifleet-nav2-hot-params :is([data-route-start], [data-testid="nav2-refresh-saved"]) {
    color: var(--accent);
    background: var(--selected);
    border-color: var(--accent);
  }
  .omnifleet-nav2-hot-params :is([data-route-stop], [data-route-clear]) { color: var(--danger); }

  .omnifleet-nav2-hot-params .panel-top {
    position: sticky;
    top: 0;
    z-index: 6;
    margin: 0 -10px 8px;
    padding: 10px;
    border-bottom: 1px solid var(--line);
    background: var(--surface);
  }
  .omnifleet-nav2-hot-params .panel-heading {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 4px 8px;
    margin-bottom: 8px;
  }
  .omnifleet-nav2-hot-params .panel-heading h3 {
    margin: 0; padding-inline-start: 8px; border-inline-start: 3px solid var(--accent);
    font-size: 1.04em; font-weight: 650;
  }
  .omnifleet-nav2-hot-params .font-toolbar {
    display: inline-flex; padding: 2px; border: 1px solid var(--line);
    border-radius: 7px; background: var(--field);
  }
  .omnifleet-nav2-hot-params .font-toolbar button {
    padding: 2px 6px; font-size: .83em; border: 0; border-radius: 4px; background: transparent;
  }
  .omnifleet-nav2-hot-params .parameter-search { position: relative; }
  .omnifleet-nav2-hot-params .parameter-search-row { display: flex; gap: 6px; align-items: stretch; }
  .omnifleet-nav2-hot-params .parameter-search-row input { flex: 1; padding: 6px 8px; }
  .omnifleet-nav2-hot-params .parameter-search-row input::placeholder { color: var(--muted); opacity: 1; }
  .omnifleet-nav2-hot-params .parameter-search-row button { flex: none; font-size: .86em; }
  .omnifleet-nav2-hot-params .parameter-search-results {
    position: absolute;
    z-index: 8;
    inset: calc(100% + 4px) 0 auto;
    max-height: min(46vh, 420px);
    overflow: auto;
    padding: 3px;
    border: 1px solid var(--line);
    border-radius: 5px;
    background: var(--surface);
    box-shadow: 0 6px 18px #0003;
  }
  .omnifleet-nav2-hot-params .parameter-search-results button {
    display: block;
    width: 100%;
    border-color: transparent;
    text-align: left;
  }
  .omnifleet-nav2-hot-params .parameter-search-empty { padding: 6px; color: var(--muted); }
  .omnifleet-nav2-hot-params .panel-views { display: flex; gap: 4px; margin-top: 9px; }
  .omnifleet-nav2-hot-params .panel-views button { flex: 1; padding: 6px; }
  .omnifleet-nav2-hot-params .parameter-categories {
    display: flex; flex-wrap: wrap; gap: 5px; margin-top: 9px;
  }
  .omnifleet-nav2-hot-params .parameter-categories button { font-size: .85em; padding: 4px 7px; }
  .omnifleet-nav2-hot-params .parameter-search-results button { padding: 9px 8px; border-bottom: 1px solid var(--line); }
  .omnifleet-nav2-hot-params .parameter-search-results button > span { display: block; font-weight: 500; }
  .omnifleet-nav2-hot-params .parameter-readout .hint { font-size: .8em; }
  .omnifleet-nav2-hot-params .parameter-readout .status.ok { padding: 0; border: 0; background: transparent; }
  .omnifleet-nav2-hot-params .parameter-readout .status { margin: 0; }
  .omnifleet-nav2-hot-params .parameter-readout :is(.status.error, .nav-diagnostic) { flex-basis: 100%; }

  .omnifleet-nav2-hot-params .parameter-readout {
    display: flex; flex-wrap: wrap; align-items: center; gap: 6px 10px;
    margin: 8px 0; padding: 6px 0; border-bottom: 1px solid var(--line);
  }
  .omnifleet-nav2-hot-params .parameter-readout button { font-size: .89em; }
  .omnifleet-nav2-hot-params :is(.status, .nav-diagnostic) {
    padding: 6px 8px;
    margin: 6px 0 0;
    border: 1px solid var(--line);
    border-radius: 4px;
    background: var(--surface);
    color: var(--muted);
    font-size: .86em;
    white-space: pre-wrap;
  }
  .omnifleet-nav2-hot-params .status.ok { color: var(--success); }
  .omnifleet-nav2-hot-params .status.error { color: var(--danger); border-color: var(--danger); }
  .omnifleet-nav2-hot-params .nav-diagnostic {
    display: grid; gap: 6px; padding: 9px 10px;
    border-inline-start: 3px solid var(--warning); border-radius: 6px;
    background: var(--field); color: var(--text); line-height: 1.55;
  }
  .omnifleet-nav2-hot-params [data-diagnostic-title] { color: var(--warning); font-weight: 650; }
  .omnifleet-nav2-hot-params .nav-diagnostic summary { color: var(--muted); }
  .omnifleet-nav2-hot-params [data-diagnostic-raw] {
    margin-top: 5px; padding: 6px; font: .95em/1.5 ui-monospace, monospace; background: var(--surface);
  }
  .omnifleet-nav2-hot-params [data-diagnostic-locate] { justify-self: start; color: var(--accent); }
  .omnifleet-nav2-hot-params :is([data-route-status], [data-bag-status], [data-testid="navigation-stack-status"]) {
    font-size: .86em;
    color: var(--muted);
  }
  .omnifleet-nav2-hot-params [data-route-status] { margin-top: 6px; max-height: 6em; overflow: auto; white-space: pre-wrap; }
  .omnifleet-nav2-hot-params [data-testid="navigation-startup-log"] {
    max-height: min(240px, 40vh);
    overflow: auto;
    margin: 6px 0;
    padding: 6px;
    border: 1px solid var(--line);
    border-radius: 4px;
    background: var(--field);
    white-space: pre-wrap;
    font: .85em/1.5 ui-monospace, monospace;
  }

  .omnifleet-nav2-hot-params :is(.major-card, .parameter-subgroup, .advanced-settings) {
    margin: 8px 0;
    border: 1px solid var(--line);
    border-radius: 8px;
    background: var(--surface);
  }
  .omnifleet-nav2-hot-params details > summary { cursor: pointer; }
  .omnifleet-nav2-hot-params :is(.major-card, .parameter-subgroup, .advanced-settings) > summary {
    display: flex;
    align-items: baseline;
    gap: 6px;
    padding: 8px 10px;
    border-radius: 7px;
    list-style: none;
    font-weight: 500;
    color: var(--text);
  }
  .omnifleet-nav2-hot-params :is(.major-card, .parameter-subgroup, .advanced-settings) > summary::-webkit-details-marker { display: none; }
  .omnifleet-nav2-hot-params :is(.major-card, .parameter-subgroup, .advanced-settings) > summary:hover { background: var(--hover); }
  .omnifleet-nav2-hot-params :is(.major-card, .parameter-subgroup, .advanced-settings) > summary::before {
    content: '';
    flex: none;
    width: 6px;
    height: 6px;
    margin-inline: 1px 3px;
    border: solid var(--muted);
    border-width: 0 1px 1px 0;
    transform: translateY(-.08em) rotate(-45deg);
  }
  .omnifleet-nav2-hot-params :is(.major-card, .parameter-subgroup, .advanced-settings)[open] > summary { border-bottom: 1px solid var(--line); }
  .omnifleet-nav2-hot-params .major-card[open] > summary { color: var(--text); background: var(--field); border-radius: 7px 7px 0 0; }
  .omnifleet-nav2-hot-params :is(.major-card, .parameter-subgroup, .advanced-settings)[open] > summary::before { transform: translateY(-.18em) rotate(45deg); }
  .omnifleet-nav2-hot-params .major-card > summary b { flex: 1; min-width: 0; }
  .omnifleet-nav2-hot-params .major-card > summary a { flex: none; font-size: .82em; font-weight: 500; }
  .omnifleet-nav2-hot-params .card-body { padding: 0 8px 5px; }
  .omnifleet-nav2-hot-params :is(.parameter-subgroup, .advanced-settings) > summary { font-size: .91em; }

  .omnifleet-nav2-hot-params .row {
    display: grid;
    grid-template-columns: minmax(0, 1fr) clamp(64px, 31cqi, 126px);
    gap: 3px 8px;
    align-items: start;
    padding: 7px 0;
  }
  .omnifleet-nav2-hot-params .row + .row { border-top: 1px solid var(--line); }
  .omnifleet-nav2-hot-params .row > .parameter-label { display: contents; }
  .omnifleet-nav2-hot-params .row .parameter-name { grid-column: 1; grid-row: 1; align-self: center; font-weight: 500; display: flex; align-items: center; flex-wrap: wrap; gap: 5px; }
  .omnifleet-nav2-hot-params .row > input { grid-column: 2; grid-row: 1; }
  .omnifleet-nav2-hot-params .row .parameter-help { grid-column: 1 / -1; grid-row: 2; font-size: .88em; color: var(--muted); }
  .omnifleet-nav2-hot-params .parameter-info {
    flex: none; width: 20px; height: 20px; padding: 0; border: 1px solid var(--line);
    border-radius: 50%; font: 12px/18px "Inter", system-ui, sans-serif;
    color: var(--muted); background: transparent;
  }
  .omnifleet-nav2-hot-params .category-heading {
    display: flex; align-items: center; justify-content: space-between; gap: 8px;
    padding: 9px 8px; color: var(--muted); font-size: .9em; font-weight: 500;
    border-bottom: 1px solid var(--line);
  }
  .omnifleet-nav2-hot-params .category-heading b { font-weight: 500; }
  .omnifleet-nav2-hot-params .category-heading a { color: inherit; text-decoration: none; }
  .omnifleet-nav2-hot-params .category-heading a:hover { color: var(--accent); text-decoration: underline; }
  .omnifleet-nav2-hot-params section.major-card[data-section-key] { border: 0; border-radius: 0; background: transparent; }

  .omnifleet-nav2-hot-params .parameter-help > p { margin: 6px 0; line-height: 1.6; }
  .omnifleet-nav2-hot-params .parameter-help:not([hidden]) { padding: 8px; border-radius: 5px; background: var(--field); }
  .omnifleet-nav2-hot-params .parameter-links,
  .omnifleet-nav2-hot-params .additional-config-links { display: flex; flex-wrap: wrap; gap: 6px 14px; margin-top: 8px; }
  .omnifleet-nav2-hot-params .parameter-technical { overflow-wrap: anywhere; }
  .omnifleet-nav2-hot-params .additional-config-links:empty { display: none; }
  .omnifleet-nav2-hot-params .parameter-source-dialog {
    width: min(1000px, 90vw); height: min(750px, 85vh); max-height: 85vh;
    padding: 0; border: 1px solid var(--line); border-radius: 10px;
    background: var(--surface); color: var(--text); font: 14px/1.5 "Inter", system-ui, sans-serif;
  }
  .omnifleet-nav2-hot-params .parameter-source-dialog[open] { display: flex; flex-direction: column; }
  .omnifleet-nav2-hot-params .parameter-source-dialog::backdrop { background: #0009; }
  .omnifleet-nav2-hot-params .parameter-source-dialog header { display: flex; align-items: start; justify-content: space-between; gap: 16px; padding: 16px; border-bottom: 1px solid var(--line); }
  .omnifleet-nav2-hot-params .parameter-source-dialog header p { margin: 4px 0 0; color: var(--muted); overflow-wrap: anywhere; }
  .omnifleet-nav2-hot-params .parameter-source-dialog pre { flex: 1; margin: 0; overflow: auto; padding: 12px 0; font: 13px/1.7 ui-monospace, monospace; }
  .omnifleet-nav2-hot-params .source-line { display: block; min-width: max-content; padding-right: 18px; }
  .omnifleet-nav2-hot-params .source-line::before { content: attr(data-line); display: inline-block; width: 5em; padding-right: 1.5em; text-align: right; color: var(--muted); user-select: none; }
  .omnifleet-nav2-hot-params .source-selected { background: var(--selected); outline: 1px solid var(--accent); }
  .omnifleet-nav2-hot-params .algorithm-row { margin: 6px 0; }
  .omnifleet-nav2-hot-params .algorithm-note { margin: 4px 0; color: var(--muted); font-size: .86em; }
  .omnifleet-nav2-hot-params .search-located-parameter { outline: 1px solid var(--accent); outline-offset: 2px; border-radius: 3px; background: var(--selected); }

  @container parameter-panel (max-width: 240px) {
    .omnifleet-nav2-hot-params .row { grid-template-columns: minmax(0, 1fr) 66px; }
  }
  
  .omnifleet-nav2-hot-params .row input[type=checkbox] { margin: 5px 3px; }
  .omnifleet-nav2-hot-params .status:empty { display: none; }
  .omnifleet-nav2-hot-params .panel-actions { display:flex; flex-wrap:wrap; gap:6px; }
  </style>
  <div class="panel-top">
    <div class="panel-heading">
      <h3>Nav2 永久参数</h3>
      <div class="font-toolbar" role="group" aria-label="面板字体大小">
        <button type="button" data-font="-1" aria-label="缩小字体">−</button>
        <button type="button" data-font="1" aria-label="放大字体">＋</button>
        <button type="button" data-font="0" aria-label="恢复原始字体大小">恢复</button>
      </div>
    </div>
    <div class="parameter-search">
      <div class="parameter-search-row">
        <input type="search" placeholder="搜索名称、英文参数或功能" aria-label="搜索参数">
        <button type="button" data-clear-search>清空</button>
      </div>
    </div>
    <div class="panel-views" role="group" aria-label="面板内容">
      <button type="button" data-view="parameters" aria-pressed="true">参数设置</button>
      <button type="button" data-view="operations" aria-pressed="false">导航操作</button>
    </div>
    <div class="parameter-categories" role="group" aria-label="参数分类"></div>
  </div>
  <div data-view-content="parameters">
    <div class="parameter-readout">
      <button data-testid="nav2-refresh-saved" type="button">刷新参数</button>
      <span class="hint">自动保存</span>
      <output class="status" role="status" data-testid="nav2-save-status"></output>
    </div>
    <div data-parameter-fields></div>
  </div>
  <div data-view-content="operations" hidden>
    <section class="major-card"><header class="category-heading">航点导航</header>
      <div class="card-body">
        <div class="panel-actions">
          <button type="button" data-route="start" data-route-start>开始航点路线</button>
          <button type="button" data-route="stop" data-route-stop>停止路线</button>
        </div>
        <output role="status" data-route-status></output>
      </div>
    </section>
  </div>`;

  const state = context.initialState || {};
  const categories = ['避障与车体','全局规划','局部控制','MOLA 两级采样','导航恢复','建图高度','全部参数'];
  const advancedPlanner = ['planner_max_iterations','forward_approach_iterations','planner_max_planning_time','forward_angle_bins'];
  const rppGroups = [
    ['速度与平顺', ['rpp_desired_linear_vel']],
    ['倒车与方向选择', ['rpp_allow_reversing']],
    ['路线跟踪', ['rpp_velocity_scaled_lookahead','rpp_lookahead_dist','rpp_min_lookahead_dist','rpp_max_lookahead_dist','rpp_lookahead_time']],
    ['弯道与障碍减速', ['rpp_use_regulated_linear_velocity_scaling','rpp_curve_radius','rpp_use_cost_regulated_linear_velocity_scaling','rpp_cost_scaling_dist','rpp_cost_scaling_gain','rpp_curve_min_speed']],
    ['到点与终点对齐', ['goal_xy_tolerance','goal_yaw_tolerance','rpp_approach_distance','rpp_approach_min_speed']],
  ];
  const sharedFields = new Set(['geometry_local_inflation_radius','costmap_scaling','geometry_local_footprint_padding']);
  const refreshRppFields = new Set(['rpp_velocity_scaled_lookahead','rpp_use_regulated_linear_velocity_scaling','rpp_use_cost_regulated_linear_velocity_scaling']);
  const categoryBar = root.querySelector('.parameter-categories');
  const search = root.querySelector('input[type=search]');
  const readout = root.querySelector('[data-testid="nav2-save-status"]');
  const refreshButton = root.querySelector('[data-testid="nav2-refresh-saved"]');
  const fieldRoot = root.querySelector('[data-parameter-fields]');
  const routeStatus = root.querySelector('[data-route-status]');
  const routePrefix = '/omnifleet_a2/waypoints/';
  const tabs = [...root.querySelectorAll('[data-view]')];
  const element = (tag,text) => {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    return node;
  };
  let fontScale = Number(state.fontScale) || 1.4;
  let category = categories.includes(state.singleCategory) ? state.singleCategory : '全局规划';
  let payload;
  let alive = true;
  let pending = 0;
  const remember = () => context.saveState?.({...state,fontScale,singleCategory:category});
  const applyFont = () => root.style.setProperty('--panel-font-scale',String(fontScale));
  applyFont();

  for (const button of root.querySelectorAll('[data-font]')) {
    button.onclick = () => {
      const direction=Number(button.dataset.font);
      fontScale = direction ? Math.max(0.8,Math.min(2.4,fontScale+direction*.1)) : 1.4;
      applyFont();
      remember();
    };
  }

  function status(message,kind='') {
    if (!alive) return;
    readout.className = 'status' + (kind ? ' ' + kind : '');
    readout.textContent = message;
  }

  async function api(options) {
    const response = await fetch('/api/nav2/parameters',{cache:'no-store',...options});
    const body = await response.json();
    if (!response.ok) throw new Error(body.error || ('HTTP '+response.status));
    return body;
  }

  function disclosure(title,body,advanced=false,open=true) {
    const details=element('details');
    details.className=advanced?'advanced-settings':'parameter-subgroup';
    details.open=open;
    details.append(element('summary',title));
    const container=element('div');
    container.className='card-body';
    container.append(...body);
    details.append(container);
    return details;
  }

  function fieldRow(field) {
    const row=element('div'); row.className='row';
    const label=element('span'); label.className='parameter-name';
    const pretty=field.label;
    const helpButton=element('button','?');
    helpButton.className='parameter-info';
    helpButton.type='button';
    helpButton.setAttribute('aria-label',pretty+'说明');
    helpButton.setAttribute('aria-expanded','false');
    label.append(element('span',pretty+(field.unit?'（'+field.unit+'）':'')),helpButton);
    const binding=field.node+' · '+field.parameter;
    const fieldName=element('div');
    if (field.help) fieldName.append(element('div',field.help));
    fieldName.append(element('div',binding));
    if (field.mixed) fieldName.append(element('div','保存值不一致，输入一个值可统一应用。'));
    fieldName.className='parameter-help';
    fieldName.hidden=true;
    helpButton.onclick=()=>{fieldName.hidden=!fieldName.hidden;helpButton.setAttribute('aria-expanded',String(!fieldName.hidden));};
    const input=element('input');
    input.setAttribute('aria-label',pretty);
    input.dataset.testid='nav2-input-'+field.id;
    const checkbox=typeof field.value==='boolean';
    input.type=checkbox?'checkbox':'number';
    function showValue() {
      if (checkbox) input.checked=field.value;
      else input.value=field.value===null?'':String(field.value);
    }
    if (!checkbox) {
      input.step=field.integer?'1':'any';
      if (field.mixed) input.placeholder='保存值不一致';
      if (['rpp_desired_linear_vel','rpp_curve_min_speed','rpp_approach_min_speed'].includes(field.id)) input.max='1.0';
      if (field.unit) input.title=field.unit;
    }
    showValue();
    async function save() {
      if (!input.checkValidity()) { input.reportValidity(); return; }
      const value=checkbox?input.checked:input.valueAsNumber;
      if ((!checkbox&&!Number.isFinite(value)) || value===field.value) {showValue();return;}
      input.disabled=true;
      pending++;
      refreshButton.disabled=true;
      status('正在保存 '+pretty+'…');
      try {
        const next=await api({method:'POST',headers:{'Content-Type':'application/json'},
                              body:JSON.stringify({id:field.id,value})});
        field.value=next.value;
        field.mixed=false;
        input.placeholder='';
        status(pretty+' · '+next.message,next.applied?'ok':'');
      } catch(error) {
        status('保存未确认 · '+error.message,'error');
      } finally {
        showValue();
        input.disabled=false;
        pending--;
        refreshButton.disabled=pending>0;
        if (refreshRppFields.has(field.id) && alive) render();
      }
    }
    input.onchange=save;
    input.onkeydown=event=>{if(event.key==='Enter'){event.preventDefault();input.blur();}};
    row.append(label,input,fieldName);
    return row;
  }

  function modeHeading(title,mode,description) {
    const section=element('section');
    section.className='major-card';
    section.dataset.sectionKey=title;
    const header=element('header');
    header.className='category-heading';
    const help=element('a','说明');
    help.href='#';
    header.append(element('b',title),help);
    const info=element('p',description);
    info.className='hint';
    help.onclick=e=>{e.preventDefault();info.hidden=!info.hidden;};
    const select=element('select');
    select.className='algorithm-row';
    select.setAttribute('aria-label',title);
    select.append(element('option',mode));
    select.disabled=true;
    const current=element('p','当前选择 '+mode);
    current.className='algorithm-note';
    section.append(header,info,select,current);
    return section;
  }

  function readonlyRow(label,value) {
    const row=element('div');row.className='row';
    row.append(element('span',label),element('output',value));
    return row;
  }

  function render() {
    if (!payload) return;
    const filter=search.value.trim().toLowerCase();
    fieldRoot.replaceChildren();
    for (const button of categoryBar.children) {
      button.setAttribute('aria-pressed',String(!filter&&button.dataset.category===category));
    }
    for (const group of categories.slice(0,-1)) {
      if (!filter && category!=='全部参数' && group!==category) continue;
      const fields=payload.fields.filter(f=>f.group===group &&
        (!filter||[f.label,f.parameter,f.node,group,f.id,f.help].join(' ').toLowerCase().includes(filter)));
      let section;
      if (group==='全局规划' && fields.length) {
        section=modeHeading('全局路径规划算法','Smac Hybrid-A*（支持倒车）',
          '在阿克曼转弯半径内搜索前进和倒车路径，使用倒车代价保留前进偏好。');
        const basic=fields.filter(f=>!advancedPlanner.includes(f.id));
        const advanced=fields.filter(f=>advancedPlanner.includes(f.id));
        if (basic.length) section.append(disclosure('避障与路线选择',basic.map(fieldRow)));
        if (advanced.length) section.append(disclosure('高级设置 · 计算与搜索（'+advanced.length+'项）',advanced.map(fieldRow),true,Boolean(filter)));
      } else if (group==='局部控制' && fields.length) {
        section=modeHeading('局部路径跟踪算法','Regulated Pure Pursuit（RPP）',
          'RPP 跟踪阿克曼路径，根据前视距离、曲率和障碍代价调节速度。');
        const checked=id=>Boolean(payload.fields.find(f=>f.id===id)?.value);
        const showField=id=>{
          if (filter) return true;
          const scaled=checked('rpp_velocity_scaled_lookahead');
          if (id==='rpp_lookahead_dist') return !scaled;
          if (['rpp_min_lookahead_dist','rpp_max_lookahead_dist','rpp_lookahead_time'].includes(id)) return scaled;
          if (id==='rpp_curve_radius') return checked('rpp_use_regulated_linear_velocity_scaling');
          if (['rpp_cost_scaling_dist','rpp_cost_scaling_gain'].includes(id)) return checked('rpp_use_cost_regulated_linear_velocity_scaling');
          return true;
        };
        for (const [name,ids] of rppGroups) {
          const rows=ids.filter(showField).map(id=>fields.find(f=>f.id===id)).filter(Boolean);
          if (rows.length) section.append(disclosure(name,rows.map(fieldRow)));
        }
      } else if (fields.length) {
        section=element('section');
        section.className='major-card';
        if (group==='避障与车体'&&!filter) {
          const points=JSON.parse(payload.footprint);
          const dimension = index => Math.round((Math.max(...points.map(p=>p[index]))-Math.min(...points.map(p=>p[index])))*100);
          const shared=fields.filter(f=>sharedFields.has(f.id));
          const separate=fields.filter(f=>!sharedFields.has(f.id));
          section.append(disclosure('远离障碍与碰撞模型',[
            ...shared.slice(0,2).map(fieldRow),
            readonlyRow('导航碰撞模型','实际车体模型'),
            readonlyRow('车体碰撞轮廓',dimension(0)+' × '+dimension(1)+' cm'),
            ...shared.slice(2).map(fieldRow),
            ...separate.map(fieldRow),
          ]));
        } else {
          const title=group==='导航恢复'?'走不通时怎么处理':group;
          section.append(disclosure(title,fields.map(fieldRow)));
        }
      } else if (!filter && group==='MOLA 两级采样') {
        const metrics=payload.mola || {};
        section=disclosure(group,[
          ...(metrics.map_sample_count===undefined ? [
            readonlyRow('ICP 与建图采样方式','共享点云'),
            readonlyRow('共享采样目标点数',metrics.sample_count ?? '—'),
          ] : [
            readonlyRow('地图采样目标点数',metrics.map_sample_count),
            readonlyRow('ICP 采样目标点数',metrics.icp_sample_count),
          ]),
          readonlyRow('采样体素尺寸',metrics.voxel_size===undefined?'—':metrics.voxel_size+' m'),
        ]);
      } else if (!filter && group==='建图高度') {
        const limits=payload.mola?.heights;
        section=disclosure('建图高度（地图坐标系 Z）',[
          readonlyRow('障碍投影最低高度',limits?limits[0]+' m':'—'),
          readonlyRow('障碍投影最高高度',limits?limits[1]+' m':'—'),
        ]);
      }
      if (section) fieldRoot.append(section);
    }
    if (filter&&!fieldRoot.childElementCount) fieldRoot.append(element('p','没有匹配的参数'));
  }

  for (const name of categories) {
    const b=element('button',name);
    b.type='button';
    b.dataset.category=name;
    b.onclick=()=>{category=name;search.value='';remember();render();};
    categoryBar.append(b);
  }
  search.oninput=render;
  root.querySelector('[data-clear-search]').onclick=()=>{search.value='';render();search.focus();};

  async function refresh() {
    if (refreshButton.disabled) return;
    refreshButton.disabled=true;
    status('正在读取车端参数…');
    try {
      payload=await api();
      if (alive) {status('');render();}
    } catch(error) {
      status('参数服务暂不可用 · '+error.message,'error');
    } finally {
      refreshButton.disabled=pending>0;
    }
  }
  refreshButton.onclick=refresh;
  void refresh();

  for (const tab of tabs) {
    tab.onclick=()=>{
      const selected=tab.dataset.view;
      for (const button of tabs) button.setAttribute('aria-pressed',String(button===tab));
      categoryBar.hidden=selected!=='parameters';
      root.querySelector('.parameter-search').hidden=selected!=='parameters';
      for (const body of root.querySelectorAll('[data-view-content]')) body.hidden=body.dataset.viewContent!==selected;
      root.scrollTop=0;
    };
  }

  for (const button of root.querySelectorAll('[data-route]')) {
    const topic=routePrefix+button.dataset.route;
    context.advertise?.(topic,'std_msgs/msg/Empty');
    button.onclick=()=>{
      try {
        if (!context.publish) throw new Error('数据源不支持发布');
        context.publish(topic,{});
        routeStatus.textContent='已发送，等待车端状态…';
      } catch(error) {routeStatus.textContent=error.message;}
    };
  }
  context.subscribe([{topic:routePrefix+'status'}]);
  context.watch('currentFrame');
  context.onRender=(event,done)=>{
    try {
      for(const item of event.currentFrame || [])if(item.topic===routePrefix+'status')routeStatus.textContent=item.message.data || '';
    } finally {done();}
  };
  return ()=>{
    alive=false;
    host.style.position=oldPosition;
    context.unadvertise?.(routePrefix+'start');
    context.unadvertise?.(routePrefix+'stop');
    context.subscribe([]);
    context.onRender=undefined;
  };
}


(()=>{let attempts=0;const timer=setInterval(()=>{
 const fiber=document.getElementById('root')?._reactRootContainer?.current;
 if(!fiber){if(++attempts>150)clearInterval(timer);return;}
 const stack=[fiber],seen=new Set();let catalog;
 while(stack.length&&!catalog){const f=stack.pop();if(!f||seen.has(f))continue;seen.add(f);
  const values=[f.memoizedProps?.value];let d=f.dependencies?.firstContext;while(d){values.push(d.memoizedValue);d=d.next;}
  for(const v of values)if(v&&typeof v.getState==='function'&&typeof v.getState().installExtension==='function'){catalog=v;break;}
  stack.push(f.child,f.sibling);
 }
 if(!catalog){if(++attempts>150)clearInterval(timer);return;}
 const name='local.omnifleet-113-panels';
 const register=()=>{
  const state=catalog.getState();
  if(state.installedPanels?.[name+'.nav2-hot-params-panel']?.registration?.initPanel===initNav2Builtin&&state.installedPanels?.[name+'.battery-voltage']?.registration?.initPanel===initBatteryVoltage&&state.installedPanels?.[name+'.ackermann-drive']?.registration?.initPanel===initAckermannDrive&&state.installedPanels?.[name+'.drive-joystick']?.registration?.initPanel===initAckermannDrive&&state.installedPanels?.[name+'.encoder-speed']?.registration?.initPanel===initEncoderSpeed&&state.installedPanels?.[name+'.speed-gauge']?.registration?.initPanel===initEncoderSpeed&&state.installedPanels?.[name+'.drive-speed']?.registration?.initPanel===initDriveSpeed&&state.installedPanels?.[name+'.steering-center']?.registration?.initPanel===initSteeringCenter&&state.installedPanels?.[name+'.steering-limit']?.registration?.initPanel===initSteeringLimit&&!state.installedPanels?.[name+'.dsh-diagnostics'])return;
  const panels={...state.installedPanels};delete panels[name+'.dsh-diagnostics'];
  panels[name+'.speed-gauge']={extensionName:name,extensionNamespace:'local',registration:{name:'speed-gauge',initPanel:initEncoderSpeed}};
  panels[name+'.encoder-speed']={extensionName:name,extensionNamespace:'local',registration:{name:'encoder-speed',initPanel:initEncoderSpeed}};
  panels[name+'.drive-speed']={extensionName:name,extensionNamespace:'local',registration:{name:'drive-speed',initPanel:initDriveSpeed}};
  panels[name+'.steering-center']={extensionName:name,extensionNamespace:'local',registration:{name:'steering-center',initPanel:initSteeringCenter}};
  panels[name+'.steering-limit']={extensionName:name,extensionNamespace:'local',registration:{name:'steering-limit',initPanel:initSteeringLimit}};
  panels[name+'.ackermann-drive']={extensionName:name,extensionNamespace:'local',registration:{name:'ackermann-drive',initPanel:initAckermannDrive}};
  panels[name+'.drive-joystick']={extensionName:name,extensionNamespace:'local',registration:{name:'drive-joystick',initPanel:initAckermannDrive}};
  panels[name+'.battery-voltage']={extensionName:name,extensionNamespace:'local',registration:{name:'battery-voltage',initPanel:initBatteryVoltage}};
  panels[name+'.nav2-hot-params-panel']={extensionName:name,extensionNamespace:'local',registration:{name:'nav2-hot-params-panel',initPanel:initNav2Builtin}};
  catalog.setState({installedExtensions:[...(state.installedExtensions||[]).filter(x=>x.id!==name),{id:name,qualifiedName:name,namespace:'local',name:'omnifleet-113-panels',publisher:'local',version:'0.1.1',displayName:'单车永久导航参数',main:'./omnifleet113-panels.js'}],installedPanels:panels});
 };
 catalog.subscribe(register);register();window.__robot113NativePanelsReady=true;clearInterval(timer);
},200);})();

})();
