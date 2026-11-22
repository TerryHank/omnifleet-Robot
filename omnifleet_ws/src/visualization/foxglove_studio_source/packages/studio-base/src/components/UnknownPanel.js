import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import EmptyState from "@foxglove/studio-base/components/EmptyState";
import withPanel from "@foxglove/studio-base/components/Panel";
import PanelToolbar from "@foxglove/studio-base/components/PanelToolbar";
import Stack from "@foxglove/studio-base/components/Stack";
function UnconnectedUnknownPanel(props) {
    const { config, saveConfig: _saveConfig } = props;
    return (_jsxs(Stack, { flex: "auto", alignItems: "center", justifyContent: "center", "data-testid": config.id, children: [_jsx(PanelToolbar, { isUnknownPanel: true }), _jsxs(EmptyState, { children: ["Unknown panel type: ", config.type, "."] })] }));
}
UnconnectedUnknownPanel.panelType = "unknown";
UnconnectedUnknownPanel.defaultConfig = {};
/**
 * An UnknownPanel stands in for missing panels. When a panel referenced in a layout is not
 * available (maybe the extension was un-installed), this panel is shown instead.
 */
export const UnknownPanel = withPanel(UnconnectedUnknownPanel);
