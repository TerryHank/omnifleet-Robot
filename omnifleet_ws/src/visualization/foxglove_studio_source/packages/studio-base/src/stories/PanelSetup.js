import { jsx as _jsx, Fragment as _Fragment, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
//
// This file incorporates work covered by the following copyright and
// permission notice:
//
//   Copyright 2018-2021 Cruise LLC
//
//   This source code is licensed under the Apache License, Version 2.0,
//   found at http://www.apache.org/licenses/LICENSE-2.0
//   You may not use this file except in compliance with the License.
import { useTheme } from "@mui/material";
import * as _ from "lodash-es";
import { useLayoutEffect, useMemo, useState, } from "react";
import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import { useTranslation } from "react-i18next";
import { Mosaic, MosaicWindow } from "react-mosaic-component";
import { createStore } from "zustand";
import MockMessagePipelineProvider from "@foxglove/studio-base/components/MessagePipeline/MockMessagePipelineProvider";
import SettingsTreeEditor from "@foxglove/studio-base/components/SettingsTreeEditor";
import AppConfigurationContext from "@foxglove/studio-base/context/AppConfigurationContext";
import { useCurrentLayoutActions } from "@foxglove/studio-base/context/CurrentLayoutContext";
import { ExtensionCatalogContext, } from "@foxglove/studio-base/context/ExtensionCatalogContext";
import PanelCatalogContext from "@foxglove/studio-base/context/PanelCatalogContext";
import { usePanelStateStore, } from "@foxglove/studio-base/context/PanelStateContext";
import * as panels from "@foxglove/studio-base/panels";
import MockCurrentLayoutProvider from "@foxglove/studio-base/providers/CurrentLayoutProvider/MockCurrentLayoutProvider";
import { PanelStateContextProvider } from "@foxglove/studio-base/providers/PanelStateContextProvider";
import TimelineInteractionStateProvider from "@foxglove/studio-base/providers/TimelineInteractionStateProvider";
import WorkspaceContextProvider from "@foxglove/studio-base/providers/WorkspaceContextProvider";
import ThemeProvider from "@foxglove/studio-base/theme/ThemeProvider";
import "react-mosaic-component/react-mosaic-component.css";
function noop() { }
function makeMockPanelCatalog(t) {
    const allPanels = [...panels.getBuiltin(t)];
    const visiblePanels = [...panels.getBuiltin(t)];
    return {
        getPanels() {
            return visiblePanels;
        },
        getPanelByType(type) {
            return allPanels.find((panel) => panel.type === type);
        },
    };
}
function MockExtensionCatalogProvider(props) {
    const value = useMemo(() => {
        return createStore(() => ({
            installExtension: async () => await Promise.reject("unsupported"),
            installedExtensions: [],
            installedMessageConverters: props.messageConverters ?? [],
            installedPanels: {},
            installedTopicAliasFunctions: [],
        }));
    }, [props.messageConverters]);
    return (_jsx(ExtensionCatalogContext.Provider, { value: value, children: props.children }));
}
export function triggerWheel(target, deltaX) {
    const event = new WheelEvent("wheel", { deltaX, bubbles: true, cancelable: true });
    target.dispatchEvent(event);
}
const MosaicWrapper = ({ children }) => {
    return (_jsx(DndProvider, { backend: HTML5Backend, children: _jsx(Mosaic, { className: "mosaic-foxglove-theme" // prevent the default mosaic theme from being applied
            , initialValue: "mock", renderTile: (_id, path) => {
                return (_jsx(MosaicWindow, { title: "", path: path, renderPreview: () => _jsx("div", {}), children: children }));
            } }) }));
};
const EmptyTree = {
    actionHandler: () => undefined,
    nodes: {},
};
function PanelWrapper({ children, includeSettings = false, settingsWidth, }) {
    const settings = usePanelStateStore((store) => {
        const trees = Object.values(store.settingsTrees);
        if (trees.length > 1) {
            throw new Error(`includeSettings requires there to be at most 1 panel, found ${trees.length}`);
        }
        return trees[0] ?? EmptyTree;
    });
    return (_jsxs(_Fragment, { children: [includeSettings && (_jsx("div", { style: { overflow: "auto", width: settingsWidth }, children: _jsx(SettingsTreeEditor, { variant: "panel", settings: settings }) })), children] }));
}
const defaultFetchAsset = async (uri, options) => {
    const response = await fetch(uri, options);
    return {
        uri,
        data: new Uint8Array(await response.arrayBuffer()),
        mediaType: response.headers.get("content-type") ?? undefined,
    };
};
function UnconnectedPanelSetup(props) {
    const { t } = useTranslation("panels");
    const mockPanelCatalog = useMemo(() => props.panelCatalog ?? makeMockPanelCatalog(t), [props.panelCatalog, t]);
    const [mockAppConfiguration] = useState(() => ({
        get() {
            return undefined;
        },
        async set() { },
        addChangeListener() { },
        removeChangeListener() { },
    }));
    const actions = useCurrentLayoutActions();
    const [initialized, setInitialized] = useState(false);
    useLayoutEffect(() => {
        if (initialized) {
            return;
        }
        const { globalVariables, userScripts, layout, savedProps } = props.fixture ?? {};
        if (globalVariables) {
            actions.overwriteGlobalVariables(globalVariables);
        }
        if (userScripts) {
            actions.setUserScripts(userScripts);
        }
        if (layout != undefined) {
            actions.changePanelLayout({ layout });
        }
        if (savedProps) {
            actions.savePanelConfigs({
                configs: Object.entries(savedProps).map(([id, config]) => ({ id, config })),
            });
        }
        setInitialized(true);
    }, [initialized, props.fixture, actions]);
    const { frame = {}, topics = [], datatypes, capabilities, profile, activeData, progress, publish, setPublishers, setSubscriptions, setParameter, fetchAsset, callService, } = props.fixture ?? {};
    let dTypes = datatypes;
    if (!dTypes) {
        const dummyDatatypes = new Map();
        for (const { schemaName } of topics) {
            if (schemaName != undefined) {
                dummyDatatypes.set(schemaName, { definitions: [] });
            }
        }
        dTypes = dummyDatatypes;
    }
    const allData = _.flatten(Object.values(frame));
    const inner = (_jsx("div", { style: { width: "100%", height: "100%", display: "flex", ...props.style }, className: props.className, children: _jsx(MockMessagePipelineProvider, { capabilities: capabilities, topics: topics, datatypes: dTypes, messages: allData, pauseFrame: props.pauseFrame, profile: profile, activeData: activeData, progress: progress, publish: publish, startPlayback: noop, pausePlayback: noop, seekPlayback: noop, setPublishers: setPublishers, setSubscriptions: setSubscriptions, setParameter: setParameter, fetchAsset: fetchAsset ?? defaultFetchAsset, callService: callService, children: _jsx(PanelCatalogContext.Provider, { value: mockPanelCatalog, children: _jsx(AppConfigurationContext.Provider, { value: mockAppConfiguration, children: _jsx(PanelWrapper, { includeSettings: props.includeSettings, settingsWidth: props.settingsWidth, children: props.children }) }) }) }) }));
    // Wait to render children until we've initialized state as requested in the fixture
    if (!initialized) {
        return ReactNull;
    }
    const { omitDragAndDrop = false } = props;
    return omitDragAndDrop ? inner : _jsx(MosaicWrapper, { children: inner });
}
export default function PanelSetup(props) {
    const theme = useTheme();
    return (_jsx(WorkspaceContextProvider, { disablePersistenceForStorybook: true, children: _jsx(TimelineInteractionStateProvider, { children: _jsx(MockCurrentLayoutProvider, { onAction: props.onLayoutAction, children: _jsx(PanelStateContextProvider, { initialState: props.fixture?.panelState, children: _jsx(MockExtensionCatalogProvider, { messageConverters: props.fixture?.messageConverters, children: _jsx(ThemeProvider, { isDark: theme.palette.mode === "dark", children: _jsx(UnconnectedPanelSetup, { ...props }) }) }) }) }) }) }));
}
