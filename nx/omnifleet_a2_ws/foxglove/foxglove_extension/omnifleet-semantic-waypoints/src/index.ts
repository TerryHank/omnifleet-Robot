import type { ExtensionContext } from "@foxglove/extension";

import { initSemanticWaypointPanel } from "./SemanticWaypointPanel";

export function activate(extensionContext: ExtensionContext): void {
  extensionContext.registerPanel({
    name: "semantic-waypoint-panel",
    initPanel: initSemanticWaypointPanel,
  });
}
