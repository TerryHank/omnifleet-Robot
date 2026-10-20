import { jsx as _jsx, Fragment as _Fragment } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { useMemo } from "react";
import { useTranslation } from "react-i18next";
import Panel from "@foxglove/studio-base/components/Panel";
import { PanelExtensionAdapter } from "@foxglove/studio-base/components/PanelExtensionAdapter";
import { useAppContext } from "@foxglove/studio-base/context/AppContext";
import { useExtensionCatalog } from "@foxglove/studio-base/context/ExtensionCatalogContext";
import PanelCatalogContext from "@foxglove/studio-base/context/PanelCatalogContext";
import * as panels from "@foxglove/studio-base/panels";
export default function PanelCatalogProvider(props) {
    const { t } = useTranslation("panels");
    const { extraPanels } = useAppContext();
    const extensionPanels = useExtensionCatalog((state) => state.installedPanels);
    const wrappedExtensionPanels = useMemo(() => {
        return Object.values(extensionPanels ?? {}).map((panel) => {
            const panelType = `${panel.extensionName}.${panel.registration.name}`;
            const PanelWrapper = (panelProps) => {
                return (_jsx(_Fragment, { children: _jsx(PanelExtensionAdapter, { config: panelProps.config, saveConfig: panelProps.saveConfig, initPanel: panel.registration.initPanel }) }));
            };
            PanelWrapper.panelType = panelType;
            PanelWrapper.defaultConfig = {};
            return {
                category: "misc",
                title: panel.registration.name,
                type: panelType,
                module: async () => ({ default: Panel(PanelWrapper) }),
                extensionNamespace: panel.extensionNamespace,
            };
        });
    }, [extensionPanels]);
    // Re-call the function when the language changes to ensure that the panel's information is successfully translated
    const builtinPanelsInfo = useMemo(() => panels.getBuiltin(t), [t]);
    const allPanels = useMemo(() => {
        return [...builtinPanelsInfo, ...wrappedExtensionPanels, ...(extraPanels ?? [])];
    }, [wrappedExtensionPanels, builtinPanelsInfo, extraPanels]);
    const panelsByType = useMemo(() => {
        const byType = new Map();
        for (const panel of allPanels) {
            const type = panel.type;
            byType.set(type, panel);
        }
        return byType;
    }, [allPanels]);
    const provider = useMemo(() => {
        return {
            getPanels() {
                return allPanels;
            },
            getPanelByType(type) {
                return panelsByType.get(type);
            },
        };
    }, [panelsByType, allPanels]);
    return (_jsx(PanelCatalogContext.Provider, { value: provider, children: props.children }));
}
