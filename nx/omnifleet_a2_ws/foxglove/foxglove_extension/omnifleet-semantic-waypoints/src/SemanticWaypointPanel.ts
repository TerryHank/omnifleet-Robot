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
};

type WaypointCatalog = {
  pending_name: string;
  localization_ready: boolean;
  lifecycle_ready: boolean;
  navigation_active: boolean;
  waypoints: SemanticWaypoint[];
};

type StringMessage = {
  data?: unknown;
};

const STATUS_TOPIC = "/omnifleet_a2/waypoints/status";
const CATALOG_TOPIC = "/omnifleet_a2/waypoints/catalog";
const NEXT_NAME_TOPIC = "/omnifleet_a2/waypoints/next_name";
const RENAME_TOPIC = "/omnifleet_a2/waypoints/rename";
const START_TOPIC = "/omnifleet_a2/waypoints/start";
const STOP_TOPIC = "/omnifleet_a2/waypoints/stop";
const UNDO_TOPIC = "/omnifleet_a2/waypoints/undo";
const CLEAR_TOPIC = "/omnifleet_a2/waypoints/clear";

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
    typeof candidate.localization_ready === "boolean" &&
    typeof candidate.lifecycle_ready === "boolean" &&
    typeof candidate.navigation_active === "boolean" &&
    Array.isArray(candidate.waypoints)
  );
}

export function initSemanticWaypointPanel(context: PanelExtensionContext): () => void {
  const root = context.panelElement;
  root.className = "omnifleet-semantic-panel";
  root.innerHTML = `
    <style>
      .omnifleet-semantic-panel { box-sizing: border-box; height: 100%; overflow: auto; padding: 14px; color: var(--fg-default, #f5f5f5); background: var(--background-default, #11151b); font: 14px/1.45 system-ui, "Microsoft YaHei", sans-serif; }
      .omnifleet-semantic-panel * { box-sizing: border-box; }
      .omnifleet-semantic-panel h2 { margin: 0 0 10px; font-size: 19px; }
      .omnifleet-semantic-panel .hint { margin: 6px 0; color: #aeb8c5; }
      .omnifleet-semantic-panel .status { margin: 10px 0; padding: 10px; border-radius: 7px; background: #1d2631; white-space: pre-wrap; }
      .omnifleet-semantic-panel .ready { color: #45d483; font-weight: 700; }
      .omnifleet-semantic-panel .waiting { color: #ffcc66; font-weight: 700; }
      .omnifleet-semantic-panel input { width: 100%; min-width: 0; padding: 9px 10px; border: 1px solid #556170; border-radius: 6px; color: inherit; background: #141b23; }
      .omnifleet-semantic-panel button { padding: 9px 10px; border: 0; border-radius: 6px; color: white; background: #3478f6; cursor: pointer; font-weight: 650; }
      .omnifleet-semantic-panel button:disabled { opacity: .45; cursor: not-allowed; }
      .omnifleet-semantic-panel .danger { background: #d84a4a; }
      .omnifleet-semantic-panel .muted { background: #566171; }
      .omnifleet-semantic-panel .name-row { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 8px; }
      .omnifleet-semantic-panel .actions { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin: 12px 0; }
      .omnifleet-semantic-panel .point-list { display: grid; gap: 8px; margin-top: 8px; }
      .omnifleet-semantic-panel .point { padding: 9px; border: 1px solid #354151; border-radius: 7px; background: #171e27; }
      .omnifleet-semantic-panel .point-title { display: flex; justify-content: space-between; gap: 8px; margin-bottom: 7px; }
      .omnifleet-semantic-panel .coords { color: #9ba7b5; font-size: 12px; white-space: nowrap; }
      .omnifleet-semantic-panel .rename-row { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 7px; }
    </style>
    <h2>单实车语义多点导航</h2>
    <div id="readiness" class="waiting">等待定位和 Nav2 就绪</div>
    <div id="status" class="status">正在连接语义航点后台……</div>
    <label for="next-name">下一个点的名称（支持中文，留空自动使用“航点N”）</label>
    <div class="name-row">
      <input id="next-name" type="text" placeholder="例如：装货区、充电站、仓库A" />
      <button id="apply-name">应用到下一个点</button>
    </div>
    <div id="pending" class="hint">下一点：自动编号</div>
    <div class="hint">应用名称后，在左侧 3D 地图使用“发布姿态”工具放置该点。</div>
    <div class="actions">
      <button id="start">开始整条路线</button>
      <button id="stop" class="danger">停止导航</button>
      <button id="undo" class="muted">撤销上一点</button>
      <button id="clear" class="muted">清空全部点</button>
    </div>
    <strong id="count">已选 0 个语义点</strong>
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
    const ready = catalog.localization_ready && catalog.lifecycle_ready;
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
    pointList.replaceChildren();

    for (const waypoint of catalog.waypoints) {
      const card = document.createElement("div");
      card.className = "point";
      const title = document.createElement("div");
      title.className = "point-title";
      const name = document.createElement("strong");
      name.textContent = `${waypoint.index}. ${waypoint.name}`;
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
      renameRow.append(renameInput, renameButton);
      card.append(title, renameRow);
      pointList.append(card);
    }
  };

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
    [START_TOPIC, "std_msgs/msg/Empty"],
    [STOP_TOPIC, "std_msgs/msg/Empty"],
    [UNDO_TOPIC, "std_msgs/msg/Empty"],
    [CLEAR_TOPIC, "std_msgs/msg/Empty"],
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
