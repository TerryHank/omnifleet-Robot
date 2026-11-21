import type { MessageEvent, PanelExtensionContext } from "@foxglove/extension";

type PanelState = {
  draftName?: string;
};

type SemanticWaypoint = {
  index: number;
  name: string;
  x: number;
  y: number;
  yaw_deg: number;
  kind?: "pass" | "stop";
  dwell_seconds?: number;
  effective_kind?: "pass" | "stop";
};

type WaypointCatalog = {
  pending_name: string;
  nav2_ready: boolean;
  navigation_active: boolean;
  waypoints: SemanticWaypoint[];
  pass_radius?: number;
  route_preview?: { state: string; planner_id: string; pose_count: number };
  execution?: { localization_status?: string; tf_age_ms?: number; phase: string; remaining_wait: number; waypoint_states: string[] };
};

type StringMessage = {
  data?: unknown;
};

const STATUS_TOPIC = "/omnifleet_t2/waypoints/status";
const CATALOG_TOPIC = "/omnifleet_t2/waypoints/catalog";
const NEXT_NAME_TOPIC = "/omnifleet_t2/waypoints/next_name";
const RENAME_TOPIC = "/omnifleet_t2/waypoints/rename";
const NAVIGATE_TO_TOPIC = "/omnifleet_t2/waypoints/navigate_to";
const START_TOPIC = "/omnifleet_t2/waypoints/start";
const STOP_TOPIC = "/omnifleet_t2/waypoints/stop";
const UNDO_TOPIC = "/omnifleet_t2/waypoints/undo";
const CLEAR_TOPIC = "/omnifleet_t2/waypoints/clear";
const UPDATE_TOPIC = "/omnifleet_t2/waypoints/update";

function messageText(event: MessageEvent): string | undefined {
  const message = event.message as StringMessage;
  return typeof message.data === "string" ? message.data : undefined;
}

function isCatalog(value: unknown): value is WaypointCatalog {
  if (typeof value !== "object" || value == undefined) {
    return false;
  }
  const candidate = value as Partial<WaypointCatalog>;
  return (
    typeof candidate.pending_name === "string" &&
    typeof candidate.nav2_ready === "boolean" &&
    typeof candidate.navigation_active === "boolean" &&
    Array.isArray(candidate.waypoints)
  );
}

export function initSemanticWaypointPanel(context: PanelExtensionContext): () => void {
  const root = context.panelElement;
  root.className = "omnifleet-semantic-panel";
  root.innerHTML = `
    <style>
      .omnifleet-semantic-panel { box-sizing: border-box; height: 100%; overflow: auto; padding: 10px; color: var(--fg-default, #f5f5f5); background: var(--background-default, #11151b); font: 13px/1.35 system-ui, "Microsoft YaHei", sans-serif; }
      .omnifleet-semantic-panel * { box-sizing: border-box; }
      .omnifleet-semantic-panel h2 { margin: 0 0 6px; font-size: 16px; }
      .omnifleet-semantic-panel .hint { margin: 4px 0; color: #aeb8c5; }
      .omnifleet-semantic-panel .status { margin: 6px 0; padding: 7px; border-radius: 6px; background: #1d2631; white-space: pre-wrap; }
      .omnifleet-semantic-panel .ready { color: #45d483; font-weight: 700; }
      .omnifleet-semantic-panel .waiting { color: #ffcc66; font-weight: 700; }
      .omnifleet-semantic-panel input { width: 100%; min-width: 0; padding: 7px 8px; border: 1px solid #556170; border-radius: 6px; color: inherit; background: #141b23; }
      .omnifleet-semantic-panel button { padding: 7px 8px; border: 0; border-radius: 6px; color: white; background: #3478f6; cursor: pointer; font-weight: 650; }
      .omnifleet-semantic-panel button:disabled { opacity: .45; cursor: not-allowed; }
      .omnifleet-semantic-panel .danger { background: #d84a4a; }
      .omnifleet-semantic-panel .muted { background: #566171; }
      .omnifleet-semantic-panel .name-row { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 8px; }
      .omnifleet-semantic-panel .actions { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin: 8px 0; }
      .omnifleet-semantic-panel .point-list { display: grid; gap: 8px; margin-top: 8px; }
      .omnifleet-semantic-panel .point { padding: 9px; border: 1px solid #354151; border-radius: 7px; background: #171e27; }
      .omnifleet-semantic-panel .point-title { display: flex; justify-content: space-between; gap: 8px; margin-bottom: 7px; }
      .omnifleet-semantic-panel .coords { color: #9ba7b5; font-size: 12px; white-space: nowrap; }
      .omnifleet-semantic-panel .rename-row { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 7px; }
      .omnifleet-semantic-panel .navigate { width: 100%; margin-top: 6px; }
      .omnifleet-semantic-panel select { width:100%; padding:6px; color:inherit; background:#141b23; }
      .omnifleet-semantic-panel .route-options { display:grid; gap:6px; margin:8px 0; }
    </style>
    <h2>本车单点／多点导航（页面卡片）</h2>
    <div id="readiness" class="waiting">等待定位和 Nav2 就绪</div>
    <div id="status" class="status">正在连接语义航点后台……</div>
    <label for="next-name">下一个点的名称（支持中文，留空自动使用“航点N”）</label>
    <div class="name-row">
      <input id="next-name" type="text" placeholder="例如：装货区、充电站、仓库A" />
      <button id="apply-name">应用到下一个点</button>
    </div>
    <div id="pending" class="hint">下一点：自动编号</div>
    <div class="hint">应用名称后，在左侧 3D 地图使用“添加多点航点”放置该点；“发布位姿”只用于单点导航。</div>
    <div class="actions">
      <button id="start">开始整条路线</button>
      <button id="stop" class="danger">停止导航</button>
      <button id="undo" class="muted">撤销上一点</button>
      <button id="clear" class="muted">清空全部点</button>
    </div>
    <strong id="count">已选 0 个语义点</strong>
    <div class="route-options">
      <label>途经半径（米）<input id="pass-radius" type="number" min="0.05" max="0.50" step="0.01" value="0.25" /></label>
      <button id="convert-pass" class="muted">将中间点改为途经点</button>
      <div class="hint">新点默认途经，旧路线保留停靠；最终点始终停车并对齐。整条预览与实际执行路径可能随最新地图更新。</div>
      <div id="route-state" class="hint"></div>
      <input id="point-search" placeholder="搜索航点名称、途经或停靠" aria-label="搜索航点" />
    </div>
    <div id="point-list" class="point-list"></div>
  `;

  const find = <T extends HTMLElement>(selector: string): T => {
    const element = root.querySelector<T>(selector);
    if (element == undefined) {
      throw new Error(`缺少面板元素：${selector}`);
    }
    return element;
  };

  const readiness = find<HTMLDivElement>("#readiness");
  const status = find<HTMLDivElement>("#status");
  const pending = find<HTMLDivElement>("#pending");
  const count = find<HTMLElement>("#count");
  const pointList = find<HTMLDivElement>("#point-list");
  const nextName = find<HTMLInputElement>("#next-name");
  const applyName = find<HTMLButtonElement>("#apply-name");
  const start = find<HTMLButtonElement>("#start");
  const stop = find<HTMLButtonElement>("#stop");
  const undo = find<HTMLButtonElement>("#undo");
  const clear = find<HTMLButtonElement>("#clear");
  const passRadius = find<HTMLInputElement>("#pass-radius");
  const convertPass = find<HTMLButtonElement>("#convert-pass");
  const routeState = find<HTMLElement>("#route-state");
  const pointSearch = find<HTMLInputElement>("#point-search");
  const filterPoints = (): void => {
    for (const card of Array.from(pointList.querySelectorAll<HTMLElement>(".point"))) {
      card.hidden = !(card.dataset.search || "").includes(pointSearch.value.trim().toLowerCase());
    }
  };
  pointSearch.addEventListener("input", filterPoints);

  const initialState = context.initialState as PanelState | undefined;
  nextName.value = initialState?.draftName ?? "";

  const showLocalStatus = (text: string): void => {
    status.textContent = text;
  };

  const publish = (topic: string, message: unknown): boolean => {
    if (context.publish == undefined) {
      showLocalStatus("当前连接不支持发送命令，请检查 Foxglove Bridge 连接");
      return false;
    }
    try {
      context.publish(topic, message);
      return true;
    } catch (error) {
      showLocalStatus(`发送失败：${String(error)}`);
      return false;
    }
  };

  const publishString = (topic: string, data: string): boolean =>
    publish(topic, { data });
  const publishEmpty = (topic: string): boolean => publish(topic, {});

  const renderCatalog = (catalog: WaypointCatalog): void => {
    const ready = catalog.nav2_ready;
    readiness.textContent = catalog.navigation_active
      ? "导航执行中"
      : ready
        ? "系统已就绪"
        : "等待定位和 Nav2 就绪";
    readiness.className = ready ? "ready" : "waiting";
    pending.textContent = catalog.pending_name
      ? `下一点：${catalog.pending_name}`
      : `下一点：航点${catalog.waypoints.length + 1}（自动编号）`;
    count.textContent = `已选 ${catalog.waypoints.length} 个语义点`;
    start.disabled = !ready || catalog.navigation_active || catalog.waypoints.length === 0;
    applyName.disabled = catalog.navigation_active;
    undo.disabled = catalog.navigation_active || catalog.waypoints.length === 0;
    clear.disabled = catalog.navigation_active || catalog.waypoints.length === 0;
    passRadius.disabled = convertPass.disabled = catalog.navigation_active;
    if (document.activeElement !== passRadius) passRadius.value = String(catalog.pass_radius ?? 0.25);
    const phases: Record<string,string> = {fleet_running:"协同正在调用本车导航，可由本地目标接管",idle:"待开始",preplanning:"整条路线检查中",tracking:"连续跟踪中",replanning:"剩余路线重规划中",stopping:"停靠对齐完成，确认停车",waiting:"停靠等待中",completed:"整条路线完成",failed:"路线失败",canceled:"已停止",canceling:"正在取消",cancel_unconfirmed:"取消未确认",preview_ready:"预规划通过",single_point:"单点导航"};
    routeState.textContent = `整条预览：${catalog.route_preview?.state ?? "等待"}（${catalog.route_preview?.planner_id ?? ""}）；执行：${phases[catalog.execution?.phase ?? "idle"] ?? catalog.execution?.phase}`;
    routeState.textContent += `；${catalog.execution?.localization_status ?? "等待定位状态"}`;
    if (catalog.execution?.phase === "waiting") routeState.textContent += `，剩余 ${catalog.execution.remaining_wait.toFixed(1)} 秒`;
    pointList.replaceChildren();

    for (const waypoint of catalog.waypoints) {
      const card = document.createElement("div");
      card.className = "point";
      const title = document.createElement("div");
      title.className = "point-title";
      const name = document.createElement("strong");
      name.textContent = `${waypoint.index}. ${waypoint.name}`;
      const final = waypoint.index === catalog.waypoints.length;
      const kind = final ? "stop" : (waypoint.kind ?? "stop");
      const stateLabel = catalog.execution?.waypoint_states?.[waypoint.index-1] ?? "待通过";
      card.dataset.search = `${waypoint.index} ${waypoint.name} ${kind === "pass" ? "途经" : "停靠"} ${final ? "终点" : ""}`.toLowerCase();
      const options = document.createElement("div"); options.className = "route-options";
      const typeLabel = document.createElement("label");typeLabel.textContent = final ? "最终点：停车并对齐" : "航点类型";
      const type = document.createElement("select"); type.setAttribute("aria-label",`第${waypoint.index}点类型`);
      for (const [value,label] of [["pass","途经：连续通过"],["stop","停靠：停车并对齐"]]) {
        const option=document.createElement("option");option.value=value!;option.textContent=label!;type.append(option);
      }
      type.value=kind;type.disabled=catalog.navigation_active || final;
      type.onchange=()=>{publishString(UPDATE_TOPIC,JSON.stringify({index:waypoint.index,kind:type.value}));};
      typeLabel.append(type);
      const dwellLabel=document.createElement("label");dwellLabel.textContent="停稳后等待（秒）";
      const dwell=document.createElement("input");dwell.type="number";dwell.min="0";dwell.max="600";dwell.step="0.1";dwell.value=String(waypoint.dwell_seconds??0);
      dwell.setAttribute("aria-label",`第${waypoint.index}点等待秒数`);dwell.disabled=catalog.navigation_active || kind==="pass";
      dwell.onchange=()=>{if(dwell.value.trim()!=="" && dwell.checkValidity())publishString(UPDATE_TOPIC,JSON.stringify({index:waypoint.index,dwell_seconds:Number(dwell.value)}));};
      dwellLabel.append(dwell);const progress=document.createElement("span");progress.textContent=stateLabel;
      options.append(typeLabel,dwellLabel,progress);
      const coords = document.createElement("span");
      coords.className = "coords";
      coords.textContent = `x ${waypoint.x.toFixed(2)}  y ${waypoint.y.toFixed(2)}  ${waypoint.yaw_deg.toFixed(0)}°`;
      title.append(name, coords);

      const renameRow = document.createElement("div");
      renameRow.className = "rename-row";
      const renameInput = document.createElement("input");
      renameInput.value = waypoint.name;
      renameInput.setAttribute("aria-label", `重命名第 ${waypoint.index} 个点`);
      const renameButton = document.createElement("button");
      renameButton.className = "muted";
      renameButton.textContent = "重命名";
      renameButton.disabled = catalog.navigation_active;
      renameButton.addEventListener("click", () => {
        publishString(
          RENAME_TOPIC,
          JSON.stringify({ index: waypoint.index, name: renameInput.value }),
        );
      });
      renameInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
          renameButton.click();
        }
      });
      const navigateButton = document.createElement("button");
      navigateButton.className = "navigate";
      navigateButton.textContent = `只导航到“${waypoint.name}”`;
      navigateButton.disabled = !ready || catalog.navigation_active;
      navigateButton.addEventListener("click", () => {
        publishString(NAVIGATE_TO_TOPIC, JSON.stringify({ index: waypoint.index }));
      });
      renameRow.append(renameInput, renameButton);
      card.append(title, options, renameRow, navigateButton);
      pointList.append(card);
    }
    filterPoints();
  };
  passRadius.onchange = () => {
    if (passRadius.value.trim()!=="" && passRadius.checkValidity()) publishString(UPDATE_TOPIC,JSON.stringify({pass_radius:Number(passRadius.value)}));
  };
  convertPass.onclick = () => {publishString(UPDATE_TOPIC,JSON.stringify({convert_intermediate:true}));};

  nextName.addEventListener("input", () => {
    context.saveState({ draftName: nextName.value });
  });
  applyName.addEventListener("click", () => {
    if (publishString(NEXT_NAME_TOPIC, nextName.value)) {
      nextName.value = "";
      context.saveState({ draftName: "" });
    }
  });
  nextName.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      applyName.click();
    }
  });
  start.addEventListener("click", () => publishEmpty(START_TOPIC));
  stop.addEventListener("click", () => publishEmpty(STOP_TOPIC));
  undo.addEventListener("click", () => publishEmpty(UNDO_TOPIC));
  clear.addEventListener("click", () => {
    if (window.confirm("确定清空全部语义点吗？")) {
      publishEmpty(CLEAR_TOPIC);
    }
  });

  const advertisedTopics: Array<[string, string]> = [
    [NEXT_NAME_TOPIC, "std_msgs/msg/String"],
    [RENAME_TOPIC, "std_msgs/msg/String"],
    [NAVIGATE_TO_TOPIC, "std_msgs/msg/String"],
    [START_TOPIC, "std_msgs/msg/Empty"],
    [STOP_TOPIC, "std_msgs/msg/Empty"],
    [UNDO_TOPIC, "std_msgs/msg/Empty"],
    [CLEAR_TOPIC, "std_msgs/msg/Empty"],
    [UPDATE_TOPIC, "std_msgs/msg/String"],
  ];
  for (const [topic, schema] of advertisedTopics) {
    context.advertise?.(topic, schema);
  }

  let previousCatalog = "";
  context.onRender = (renderState, done) => {
    try {
      for (const event of renderState.currentFrame ?? []) {
        if (event.topic === STATUS_TOPIC) {
          const text = messageText(event);
          if (text != undefined) {
            status.textContent = text;
          }
        } else if (event.topic === CATALOG_TOPIC) {
          const text = messageText(event);
          if (text != undefined && text !== previousCatalog) {
            try {
              const catalog: unknown = JSON.parse(text);
              if (isCatalog(catalog)) {
                previousCatalog = text;
                renderCatalog(catalog);
              }
            } catch (error) {
              showLocalStatus(`航点目录解析失败：${String(error)}`);
            }
          }
        }
      }
    } finally {
      done();
    }
  };
  context.watch("currentFrame");
  context.subscribe([{ topic: STATUS_TOPIC }, { topic: CATALOG_TOPIC }]);

  return () => {
    context.subscribe([]);
    for (const [topic] of advertisedTopics) {
      context.unadvertise?.(topic);
    }
    root.replaceChildren();
  };
}
