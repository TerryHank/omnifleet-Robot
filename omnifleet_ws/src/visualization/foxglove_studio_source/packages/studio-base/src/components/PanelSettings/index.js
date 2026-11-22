import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { Divider, Typography } from "@mui/material";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { useUnmount } from "react-use";
import { useConfigById } from "@foxglove/studio-base/PanelAPI";
import EmptyState from "@foxglove/studio-base/components/EmptyState";
import { ActionMenu } from "@foxglove/studio-base/components/PanelSettings/ActionMenu";
import SettingsTreeEditor from "@foxglove/studio-base/components/SettingsTreeEditor";
import { ShareJsonModal } from "@foxglove/studio-base/components/ShareJsonModal";
import Stack from "@foxglove/studio-base/components/Stack";
import { useCurrentLayoutActions, useCurrentLayoutSelector, useSelectedPanels, } from "@foxglove/studio-base/context/CurrentLayoutContext";
import { usePanelCatalog } from "@foxglove/studio-base/context/PanelCatalogContext";
import { usePanelStateStore, } from "@foxglove/studio-base/context/PanelStateContext";
import { TAB_PANEL_TYPE } from "@foxglove/studio-base/util/globalConstants";
import { getPanelTypeFromId } from "@foxglove/studio-base/util/layout";
const singlePanelIdSelector = (state) => typeof state.selectedLayout?.data?.layout === "string"
    ? state.selectedLayout.data.layout
    : undefined;
const selectIncrementSequenceNumber = (store) => store.incrementSequenceNumber;
const EMPTY_SETTINGS_TREE = Object.freeze({
    actionHandler: () => undefined,
    nodes: {},
});
export default function PanelSettings({ selectedPanelIdsForTests, }) {
    const { t } = useTranslation("panelSettings");
    const singlePanelId = useCurrentLayoutSelector(singlePanelIdSelector);
    const { selectedPanelIds: originalSelectedPanelIds, setSelectedPanelIds, selectAllPanels, } = useSelectedPanels();
    const selectedPanelIds = selectedPanelIdsForTests ?? originalSelectedPanelIds;
    // If no panel is selected and there is only one panel in the layout, select it
    useEffect(() => {
        if (selectedPanelIds.length === 0 && singlePanelId != undefined) {
            selectAllPanels();
        }
    }, [selectAllPanels, selectedPanelIds, singlePanelId]);
    const selectedPanelId = useMemo(() => (selectedPanelIds.length === 1 ? selectedPanelIds[0] : undefined), [selectedPanelIds]);
    // Automatically deselect the panel we were editing when the settings sidebar closes
    useUnmount(() => {
        if (selectedPanelId != undefined) {
            setSelectedPanelIds([]);
        }
    });
    const panelCatalog = usePanelCatalog();
    const { getCurrentLayoutState: getCurrentLayout, savePanelConfigs } = useCurrentLayoutActions();
    const panelType = useMemo(() => (selectedPanelId != undefined ? getPanelTypeFromId(selectedPanelId) : undefined), [selectedPanelId]);
    const panelInfo = useMemo(() => (panelType != undefined ? panelCatalog.getPanelByType(panelType) : undefined), [panelCatalog, panelType]);
    const incrementSequenceNumber = usePanelStateStore(selectIncrementSequenceNumber);
    const [showShareModal, setShowShareModal] = useState(false);
    const shareModal = useMemo(() => {
        const panelConfigById = getCurrentLayout().selectedLayout?.data?.configById;
        if (selectedPanelId == undefined || !showShareModal || !panelConfigById) {
            return ReactNull;
        }
        return (_jsx(ShareJsonModal, { onRequestClose: () => {
                setShowShareModal(false);
            }, initialValue: panelConfigById[selectedPanelId] ?? {}, onChange: (config) => {
                savePanelConfigs({
                    configs: [{ id: selectedPanelId, config: config, override: true }],
                });
                incrementSequenceNumber(selectedPanelId);
            }, title: t("importOrExportSettings") }));
    }, [
        getCurrentLayout,
        selectedPanelId,
        showShareModal,
        savePanelConfigs,
        incrementSequenceNumber,
        t,
    ]);
    const [config] = useConfigById(selectedPanelId);
    const settingsTree = usePanelStateStore((state) => selectedPanelId ? state.settingsTrees[selectedPanelId] : undefined);
    const resetToDefaults = useCallback(() => {
        if (selectedPanelId) {
            savePanelConfigs({
                configs: [{ id: selectedPanelId, config: {}, override: true }],
            });
            incrementSequenceNumber(selectedPanelId);
        }
    }, [incrementSequenceNumber, savePanelConfigs, selectedPanelId]);
    if (selectedPanelId == undefined) {
        return _jsx(EmptyState, { children: t("selectAPanelToEditItsSettings") });
    }
    if (!config) {
        return _jsx(EmptyState, { children: t("loadingPanelSettings") });
    }
    const showTitleField = panelInfo != undefined && panelInfo.hasCustomToolbar !== true;
    const title = panelInfo?.title ?? t("unknown");
    return (_jsxs(Stack, { fullHeight: true, flex: "auto", gap: 1, children: [shareModal, _jsx(Stack, { gap: 2, justifyContent: "flex-start", flex: "auto", children: _jsxs(Stack, { flex: "auto", children: [settingsTree && (_jsxs(_Fragment, { children: [_jsxs(Stack, { paddingLeft: 0.75, direction: "row", alignItems: "center", justifyContent: "space-between", children: [_jsx(Typography, { variant: "subtitle2", children: t("panelName", { title }) }), _jsx(ActionMenu, { fontSize: "small", allowShare: panelType !== TAB_PANEL_TYPE, onReset: resetToDefaults, onShare: () => {
                                                setShowShareModal(true);
                                            } }, 1)] }), _jsx(Divider, {})] })), settingsTree != undefined || showTitleField ? (_jsx(SettingsTreeEditor, { variant: "panel", settings: settingsTree ?? EMPTY_SETTINGS_TREE }, selectedPanelId)) : (_jsx(Stack, { flex: "auto", alignItems: "center", justifyContent: "center", paddingX: 1, children: _jsx(Typography, { variant: "body2", color: "text.secondary", align: "center", children: t("panelDoesNotHaveSettings") }) }))] }) })] }));
}
