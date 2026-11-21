import { initFleetPanel } from "./FleetPanel.js";
import type { ExtensionContext } from "@foxglove/extension";

import { initSemanticWaypointPanel } from "./SemanticWaypointPanel";
import { initNav2HotParamsPanel } from "./Nav2HotParamsPanel";

export function activate(extensionContext: ExtensionContext): void {
  extensionContext.registerPanel({
    name: "semantic-waypoint-panel",
    initPanel: initSemanticWaypointPanel,
  });
  extensionContext.registerPanel({
    name: "nav2-hot-params-panel",
    initPanel: initNav2HotParamsPanel,
  });
  extensionContext.registerPanel({name:"fleet-panel",initPanel:initFleetPanel});
}
