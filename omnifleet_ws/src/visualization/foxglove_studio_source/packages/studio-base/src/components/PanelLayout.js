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
import { CircularProgress } from "@mui/material";
import React, { Suspense, useCallback, useMemo } from "react";
import { useDrop } from "react-dnd";
import { MosaicDragType, MosaicWindow, MosaicWithoutDragDropContext, } from "react-mosaic-component";
import { makeStyles } from "tss-react/mui";
import { EmptyPanelLayout } from "@foxglove/studio-base/components/EmptyPanelLayout";
import EmptyState from "@foxglove/studio-base/components/EmptyState";
import Stack from "@foxglove/studio-base/components/Stack";
import { useAppContext } from "@foxglove/studio-base/context/AppContext";
import { useCurrentLayoutActions, useCurrentLayoutSelector, usePanelMosaicId, } from "@foxglove/studio-base/context/CurrentLayoutContext";
import { useExtensionCatalog } from "@foxglove/studio-base/context/ExtensionCatalogContext";
import { usePanelCatalog } from "@foxglove/studio-base/context/PanelCatalogContext";
import { getPanelIdForType, getPanelTypeFromId } from "@foxglove/studio-base/util/layout";
import ErrorBoundary from "./ErrorBoundary";
import { MosaicPathContext } from "./MosaicPathContext";
import { PanelRemounter } from "./PanelRemounter";
import { UnknownPanel } from "./UnknownPanel";
import "react-mosaic-component/react-mosaic-component.css";
// CSS hack to disable the first level of drop targets inside a Tab's own mosaic window (that would
// place the dropped item as a sibling of the Tab), as well as the "root drop targets" inside the
// nested mosaic (that would place the dropped item as a direct child of the Tab). Makes it easier
// to drop panels into a tab layout.
const useStyles = makeStyles()({
    hideTopLevelDropTargets: {
        margin: 0,
        ".mosaic-root + .drop-target-container": {
            display: "none !important",
        },
        "& > .mosaic-window > .drop-target-container": {
            display: "none !important",
        },
    },
});
// This wrapper makes the tabId available in the drop result when something is dropped into a nested
// drop target. This allows a panel to know which mosaic it was dropped in regardless of nesting
// level.
function TabMosaicWrapper({ tabId, children }) {
    const { classes, cx } = useStyles();
    const [, drop] = useDrop({
        accept: MosaicDragType.WINDOW,
        drop: (_item, monitor) => {
            const nestedDropResult = monitor.getDropResult();
            // MosaicWindow has a top-level drop target which can fire if something is dropped onto the
            // tab bar or elsewhere inside the tab that doesn't correspond to one of the other mosaic drop
            // targets. In this case we don't want to replace the tab's existing layout so we do nothing.
            if (nestedDropResult?.path == undefined) {
                return undefined;
            }
            // The drop result may already have a tabId if it was dropped in a more deeply-nested Tab
            // mosaic. Provide our tabId only if there wasn't one already.
            return { tabId, ...nestedDropResult };
        },
    });
    return (_jsx("div", { className: cx(classes.hideTopLevelDropTargets, "mosaic-tile"), ref: drop, children: children }));
}
export function UnconnectedPanelLayout(props) {
    const { savePanelConfigs } = useCurrentLayoutActions();
    const mosaicId = usePanelMosaicId();
    const { layout, onChange, tabId } = props;
    const createTile = useCallback((config) => {
        const defaultPanelType = "RosOut";
        const type = config?.type ? config.type : defaultPanelType;
        const id = getPanelIdForType(type);
        if (config?.panelConfig) {
            savePanelConfigs({ configs: [{ id, config: config.panelConfig }] });
        }
        return id;
    }, [savePanelConfigs]);
    const panelCatalog = usePanelCatalog();
    const panelComponents = useMemo(() => new Map(panelCatalog.getPanels().map((panelInfo) => [panelInfo.type, React.lazy(panelInfo.module)])), [panelCatalog]);
    const renderTile = useCallback((id, path) => {
        // `id` is usually a string. But when `layout` is empty, `id` will be an empty object, in which case we don't need to render Tile
        if (id == undefined || typeof id !== "string") {
            return _jsx(_Fragment, {});
        }
        const type = getPanelTypeFromId(id);
        let panel;
        const PanelComponent = panelComponents.get(type);
        if (PanelComponent) {
            panel = _jsx(PanelComponent, { childId: id, tabId: tabId });
        }
        else {
            // If we haven't found a panel of the given type, render the panel selector
            panel = _jsx(UnknownPanel, { childId: id, tabId: tabId, overrideConfig: { type, id } });
        }
        const mosaicWindow = (_jsx(MosaicWindow, { title: "", path: path, createNode: createTile, renderPreview: () => undefined, children: _jsx(Suspense, { fallback: _jsx(EmptyState, { children: _jsx(CircularProgress, { size: 28 }) }), children: _jsx(MosaicPathContext.Provider, { value: path, children: _jsx(PanelRemounter, { id: id, tabId: tabId, children: panel }) }) }) }, id));
        if (type === "Tab") {
            return _jsx(TabMosaicWrapper, { tabId: id, children: mosaicWindow });
        }
        return mosaicWindow;
    }, [panelComponents, createTile, tabId]);
    const bodyToRender = useMemo(() => layout != undefined ? (_jsx(MosaicWithoutDragDropContext, { renderTile: renderTile, className: "mosaic-foxglove-theme" // prevent the default mosaic theme from being applied
        , resize: { minimumPaneSizePercentage: 2 }, value: layout, onChange: (newLayout) => {
            onChange(newLayout ?? undefined);
        }, mosaicId: mosaicId })) : (_jsx(EmptyPanelLayout, { tabId: tabId })), [layout, mosaicId, onChange, renderTile, tabId]);
    return _jsx(ErrorBoundary, { children: bodyToRender });
}
function ExtensionsLoadingState() {
    return (_jsx(EmptyState, { children: _jsxs(Stack, { gap: 1, alignItems: "center", children: [_jsx(CircularProgress, { size: 28 }), _jsx("span", { children: "Loading extensions\u2026" })] }) }));
}
const selectedLayoutExistsSelector = (state) => state.selectedLayout?.data != undefined;
const selectedLayoutMosaicSelector = (state) => state.selectedLayout?.data?.layout;
export default function PanelLayout() {
    const { layoutEmptyState } = useAppContext();
    const { changePanelLayout } = useCurrentLayoutActions();
    const layoutExists = useCurrentLayoutSelector(selectedLayoutExistsSelector);
    const mosaicLayout = useCurrentLayoutSelector(selectedLayoutMosaicSelector);
    const registeredExtensions = useExtensionCatalog((state) => state.installedExtensions);
    const onChange = useCallback((newLayout) => {
        if (newLayout != undefined) {
            changePanelLayout({ layout: newLayout });
        }
    }, [changePanelLayout]);
    if (registeredExtensions == undefined) {
        return _jsx(ExtensionsLoadingState, {});
    }
    if (layoutExists) {
        return _jsx(UnconnectedPanelLayout, { layout: mosaicLayout, onChange: onChange });
    }
    if (layoutEmptyState) {
        return layoutEmptyState;
    }
    return _jsx(_Fragment, {});
}
