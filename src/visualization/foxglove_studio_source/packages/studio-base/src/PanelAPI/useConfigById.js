// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { useCallback } from "react";
import { useCurrentLayoutActions, useCurrentLayoutSelector, } from "@foxglove/studio-base/context/CurrentLayoutContext";
import { maybeCast } from "@foxglove/studio-base/util/maybeCast";
/**
 * Like `useConfig`, but for a specific panel id. This generally shouldn't be used by panels
 * directly, but is for use in internal code that's running outside of regular context providers.
 */
export default function useConfigById(panelId) {
    const { getCurrentLayoutState, savePanelConfigs } = useCurrentLayoutActions();
    const configSelector = useCallback((state) => {
        if (panelId == undefined) {
            return undefined;
        }
        return maybeCast(state.selectedLayout?.data?.configById?.[panelId]);
    }, [panelId]);
    const config = useCurrentLayoutSelector(configSelector);
    const saveConfig = useCallback((newConfig) => {
        if (panelId == undefined) {
            return;
        }
        if (typeof newConfig === "function") {
            // We use a getter here instead of referring directly to the config object
            // so that this callback is stable across config changes.
            const currentConfig = getCurrentLayoutState().selectedLayout?.data?.configById[panelId];
            if (currentConfig) {
                savePanelConfigs({
                    configs: [{ id: panelId, config: newConfig(currentConfig) }],
                });
            }
        }
        else {
            savePanelConfigs({
                configs: [{ id: panelId, config: newConfig }],
            });
        }
    }, [getCurrentLayoutState, panelId, savePanelConfigs]);
    return [config, saveConfig];
}
