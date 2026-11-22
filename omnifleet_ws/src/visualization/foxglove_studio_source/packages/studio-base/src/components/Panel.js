import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
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
import { Delete20Regular, TabDesktop20Regular, TabDesktopMultiple20Regular, TableSimple20Regular, } from "@fluentui/react-icons";
import * as _ from "lodash-es";
import React, { Profiler, useCallback, useContext, useLayoutEffect, useMemo, useRef, useState, } from "react";
import { getNodeAtPath, getOtherBranch, MosaicContext, MosaicWindowContext, updateTree, } from "react-mosaic-component";
import { Transition } from "react-transition-group";
import { useMountedState } from "react-use";
import { makeStyles } from "tss-react/mui";
import { useShallowMemo } from "@foxglove/hooks";
import { useConfigById } from "@foxglove/studio-base/PanelAPI";
import KeyListener from "@foxglove/studio-base/components/KeyListener";
import { MosaicPathContext } from "@foxglove/studio-base/components/MosaicPathContext";
import PanelContext from "@foxglove/studio-base/components/PanelContext";
import PanelErrorBoundary from "@foxglove/studio-base/components/PanelErrorBoundary";
import { PanelOverlay } from "@foxglove/studio-base/components/PanelOverlay";
import { PanelRoot } from "@foxglove/studio-base/components/PanelRoot";
import { useCurrentLayoutActions, useSelectedPanels, } from "@foxglove/studio-base/context/CurrentLayoutContext";
import { usePanelCatalog } from "@foxglove/studio-base/context/PanelCatalogContext";
import { useWorkspaceStore, WorkspaceStoreSelectors, } from "@foxglove/studio-base/context/Workspace/WorkspaceContext";
import usePanelDrag from "@foxglove/studio-base/hooks/usePanelDrag";
import { useMessagePathDrop } from "@foxglove/studio-base/services/messagePathDragging";
import { TAB_PANEL_TYPE } from "@foxglove/studio-base/util/globalConstants";
import { getPanelIdForType, getPanelTypeFromId, getPathFromNode, updateTabPanelLayout, } from "@foxglove/studio-base/util/layout";
const useStyles = makeStyles()((theme) => ({
    perfInfo: {
        position: "absolute",
        bottom: 2,
        left: 3,
        whiteSpace: "pre-line",
        fontSize: "0.75em",
        fontFeatureSettings: `${theme.typography.fontFeatureSettings}, 'zero'`,
        opacity: 0.7,
        userSelect: "none",
        mixBlendMode: "difference",
    },
    tabCount: {
        alignItems: "center",
        justifyContent: "center",
        position: "absolute",
        display: "flex",
        inset: 0,
        textAlign: "center",
        letterSpacing: "-0.125em",
        // Totally random numbers here to get the text to fit inside the icon
        paddingTop: 1,
        paddingLeft: 5,
        paddingRight: 11,
        fontSize: `${theme.typography.subtitle2.fontSize} !important`,
        fontWeight: 600,
    },
}));
/** Used in storybook when panels are renered outside of a <PanelLayout/> */
const FALLBACK_PANEL_ID = "$unknown_id";
// HOC that wraps panel in an error boundary and flex box.
// Gives panel a `config` and `saveConfig`.
//   export default Panel(MyPanelComponent)
//
// `config` comes from the current layout, but in stories / tests you can pass in your own:
//   `<MyPanel config={…} />`
export default function Panel(PanelComponent) {
    function ConnectedPanel(props) {
        const { childId = FALLBACK_PANEL_ID, overrideConfig, tabId, ...otherProps } = props;
        const { classes, cx, theme } = useStyles();
        const isMounted = useMountedState();
        const { mosaicActions } = useContext(MosaicContext);
        const { mosaicWindowActions } = useContext(MosaicWindowContext);
        const { selectedPanelIds, setSelectedPanelIds, selectAllPanels, togglePanelSelected, getSelectedPanelIds, } = useSelectedPanels();
        const isSelected = useMemo(() => selectedPanelIds.includes(childId), [childId, selectedPanelIds]);
        const numSelectedPanelsIfSelected = useMemo(() => (isSelected ? selectedPanelIds.length : 0), [isSelected, selectedPanelIds]);
        const { savePanelConfigs, updatePanelConfigs, createTabPanel, closePanel, swapPanel, getCurrentLayoutState, } = useCurrentLayoutActions();
        const [quickActionsKeyPressed, setQuickActionsKeyPressed] = useState(false);
        const [fullscreen, setFullscreen] = useState(false);
        const [fullscreenSourceRect, setFullscreenSourceRect] = useState(undefined);
        const [hasFullscreenDescendant, _setHasFullscreenDescendant] = useState(false);
        const panelRootRef = useRef(ReactNull);
        const panelCatalog = usePanelCatalog();
        const mosaicPath = useContext(MosaicPathContext);
        const isTopLevelPanel = mosaicPath != undefined && mosaicPath.length === 0 && tabId == undefined;
        // There may be a parent panel (when a panel is in a tab).
        const parentPanelContext = useContext(PanelContext);
        const type = PanelComponent.panelType;
        const title = useMemo(() => panelCatalog.getPanelByType(type)?.title ?? "", [panelCatalog, type]);
        const defaultConfig = PanelComponent.defaultConfig;
        const [savedConfig, saveConfig] = useConfigById(childId);
        const resetPanel = useCallback(() => {
            saveConfig(defaultConfig);
        }, [defaultConfig, saveConfig]);
        // PanelSettings needs useConfigById to return a complete config. If there is no saved config
        // (or it is an empty object), or if keys have been added to the default config since it was
        // previously saved, we save the default config provided by the panel. This typically happens
        // when a new panel is added and the layout does not yet have a config. Even if this effect gets
        // run more than once, we only need to save the default config once.
        //
        // An empty object can occur when swapping a panel
        const savedDefaultConfig = useRef(false);
        useLayoutEffect(() => {
            if (savedDefaultConfig.current) {
                return;
            }
            if (!savedConfig || Object.keys(savedConfig).length === 0) {
                savedDefaultConfig.current = true;
                saveConfig(defaultConfig);
            }
            else if (Object.entries(defaultConfig).some(([key, value]) => value != undefined && !(key in savedConfig))) {
                savedDefaultConfig.current = true;
                saveConfig({ ...defaultConfig, ...savedConfig });
            }
        }, [defaultConfig, saveConfig, savedConfig]);
        const panelComponentConfig = useMemo(() => ({ ...defaultConfig, ...savedConfig, ...overrideConfig }), [savedConfig, defaultConfig, overrideConfig]);
        // Open a panel next to the current panel, of the specified `panelType`.
        // If such a panel already exists, we update it with the new props.
        const openSiblingPanel = useCallback(async ({ panelType, siblingConfigCreator, updateIfExists }) => {
            const panelsState = getCurrentLayoutState().selectedLayout?.data;
            if (!panelsState) {
                return;
            }
            let siblingDefaultConfig = {};
            // If we can lookup the sibling panel type, try to load the default config from the panel module
            const siblingPanelInfo = panelCatalog.getPanelByType(panelType);
            if (siblingPanelInfo) {
                const siblingModule = await siblingPanelInfo.module();
                if (!isMounted()) {
                    return;
                }
                siblingDefaultConfig = siblingModule.default.defaultConfig;
            }
            const ownPath = mosaicWindowActions.getPath();
            // Try to find a sibling panel and update it with the `siblingConfig`
            if (updateIfExists) {
                const lastNode = _.last(ownPath);
                const siblingPathEnd = lastNode != undefined ? getOtherBranch(lastNode) : "second";
                const siblingPath = ownPath.slice(0, -1).concat(siblingPathEnd);
                const siblingId = getNodeAtPath(mosaicActions.getRoot(), siblingPath);
                if (typeof siblingId === "string" && getPanelTypeFromId(siblingId) === panelType) {
                    const siblingConfig = {
                        ...siblingDefaultConfig,
                        ...panelsState.configById[siblingId],
                    };
                    savePanelConfigs({
                        configs: [
                            {
                                id: siblingId,
                                config: siblingConfigCreator(siblingConfig),
                                defaultConfig: siblingDefaultConfig,
                            },
                        ],
                    });
                    return;
                }
            }
            // Otherwise, open new panel
            const newPanelPath = ownPath.concat("second");
            const newPanelConfig = siblingConfigCreator(siblingDefaultConfig);
            void mosaicWindowActions
                .split({ type: panelType, panelConfig: newPanelConfig })
                .then(() => {
                const newPanelId = getNodeAtPath(mosaicActions.getRoot(), newPanelPath);
                savePanelConfigs({
                    configs: [
                        {
                            id: newPanelId,
                            config: newPanelConfig,
                            defaultConfig: siblingDefaultConfig,
                        },
                    ],
                });
            });
        }, [
            getCurrentLayoutState,
            isMounted,
            mosaicActions,
            mosaicWindowActions,
            panelCatalog,
            savePanelConfigs,
        ]);
        const replacePanel = useCallback((newPanelType, config) => {
            swapPanel({
                tabId,
                originalId: childId,
                type: newPanelType,
                root: mosaicActions.getRoot(),
                path: mosaicWindowActions.getPath(),
                config,
            });
        }, [childId, mosaicActions, mosaicWindowActions, swapPanel, tabId]);
        const panelSettingsOpen = useWorkspaceStore(WorkspaceStoreSelectors.selectPanelSettingsOpen);
        const onPanelRootClick = useCallback((e) => {
            if (panelSettingsOpen) {
                // Allow clicking with no modifiers to select a panel (and deselect others) when panel settings are open
                e.stopPropagation(); // select the deepest clicked panel, not parent tab panels
                setSelectedPanelIds([childId]);
            }
            else if (e.metaKey || e.shiftKey || isSelected) {
                e.stopPropagation(); // select the deepest clicked panel, not parent tab panels
                togglePanelSelected(childId, tabId);
            }
        }, [childId, tabId, togglePanelSelected, isSelected, setSelectedPanelIds, panelSettingsOpen]);
        const groupPanels = useCallback(() => {
            const layout = getCurrentLayoutState().selectedLayout?.data?.layout;
            if (layout == undefined) {
                return;
            }
            createTabPanel({
                idToReplace: childId,
                layout,
                idsToRemove: getSelectedPanelIds(),
                singleTab: true,
            });
        }, [getCurrentLayoutState, getSelectedPanelIds, createTabPanel, childId]);
        const createTabs = useCallback(() => {
            const layout = getCurrentLayoutState().selectedLayout?.data?.layout;
            if (layout == undefined) {
                return;
            }
            createTabPanel({
                idToReplace: childId,
                layout,
                idsToRemove: getSelectedPanelIds(),
                singleTab: false,
            });
        }, [getCurrentLayoutState, getSelectedPanelIds, createTabPanel, childId]);
        const removePanel = useCallback(() => {
            closePanel({
                path: mosaicWindowActions.getPath(),
                root: mosaicActions.getRoot(),
                tabId,
            });
        }, [closePanel, mosaicActions, mosaicWindowActions, tabId]);
        const splitPanel = useCallback(() => {
            const savedProps = getCurrentLayoutState().selectedLayout?.data?.configById;
            if (!savedProps) {
                return;
            }
            const tabSavedProps = tabId != undefined ? savedProps[tabId] : undefined;
            if (tabId != undefined && tabSavedProps != undefined) {
                const newId = getPanelIdForType(PanelComponent.panelType);
                const activeTabLayout = tabSavedProps.tabs[tabSavedProps.activeTabIdx]?.layout;
                if (activeTabLayout == undefined) {
                    return;
                }
                const pathToPanelInTab = getPathFromNode(childId, activeTabLayout);
                const newTabLayout = updateTree(activeTabLayout, [
                    {
                        path: pathToPanelInTab,
                        spec: { $set: { first: childId, second: newId, direction: "row" } },
                    },
                ]);
                const newTabConfig = updateTabPanelLayout(newTabLayout, tabSavedProps);
                savePanelConfigs({
                    configs: [
                        { id: tabId, config: newTabConfig },
                        { id: newId, config: panelComponentConfig },
                    ],
                });
            }
            else {
                void mosaicWindowActions.split({ type: PanelComponent.panelType });
            }
        }, [
            childId,
            getCurrentLayoutState,
            mosaicWindowActions,
            panelComponentConfig,
            savePanelConfigs,
            tabId,
        ]);
        const { enterFullscreen, exitFullscreen } = useMemo(() => ({
            enterFullscreen: () => {
                setFullscreenSourceRect(panelRootRef.current?.getBoundingClientRect());
                setFullscreen(true);
                // When entering fullscreen for a panel within a tab, we need to adjust the ancestor
                // tab(s)'s z-index to have our panel properly overlay other panels outside the tab.
                parentPanelContext?.setHasFullscreenDescendant(true);
            },
            exitFullscreen: () => {
                // Don't clear fullscreenSourceRect or hasFullscreenDescendant, they are needed during the exit transition
                setFullscreen(false);
            },
        }), [parentPanelContext]);
        const setHasFullscreenDescendant = useCallback(
        // eslint-disable-next-line @foxglove/no-boolean-parameters
        (value) => {
            _setHasFullscreenDescendant(value);
            parentPanelContext?.setHasFullscreenDescendant(value);
        }, [parentPanelContext]);
        const { isDragging, isOver, isValidTarget, connectMessagePathDropTarget, dropMessage, setMessagePathDropConfig, } = useMessagePathDrop();
        // We use two separate sets of key handlers because the panel context and exitFullScreen
        // change often and invalidate our key handlers during user interactions.
        const { keyUpHandlers, keyDownHandlers } = useMemo(() => ({
            keyUpHandlers: {
                Backquote: () => {
                    setQuickActionsKeyPressed(false);
                },
                "~": () => {
                    setQuickActionsKeyPressed(false);
                },
            },
            keyDownHandlers: {
                a: (e) => {
                    e.preventDefault();
                    if (e.metaKey) {
                        selectAllPanels();
                    }
                },
                Backquote: () => {
                    setQuickActionsKeyPressed(true);
                },
                "~": () => {
                    setQuickActionsKeyPressed(true);
                },
                Escape: () => {
                    if (numSelectedPanelsIfSelected > 1) {
                        setSelectedPanelIds([]);
                    }
                },
            },
        }), [selectAllPanels, numSelectedPanelsIfSelected, setSelectedPanelIds]);
        const fullScreenKeyHandlers = useMemo(() => ({
            Escape: () => {
                exitFullscreen();
            },
        }), [exitFullscreen]);
        const otherPanelProps = useShallowMemo(otherProps);
        const childProps = useMemo(
        // We have to lie to TypeScript with "as PanelProps" because the "PanelProps extends {...}"
        // constraint technically allows the panel to require the types of config/saveConfig be more
        // specific types that aren't satisfied by the functions we pass in
        () => ({ config: panelComponentConfig, saveConfig, ...otherPanelProps }), [otherPanelProps, panelComponentConfig, saveConfig]);
        const child = useMemo(() => _jsx(PanelComponent, { ...childProps }), [childProps]);
        const renderCount = useRef(0);
        const perfInfo = useRef(ReactNull);
        const quickActionsOverlayRef = useRef(ReactNull);
        const onDragStart = useCallback(() => {
            // Temporarily hide the overlay so that the panel can be shown as the drag preview image --
            // even though the overlay is a sibling rather than a child, Chrome still includes it in the
            // preview if it is visible. Changing the appearance in the next React render cycle is not
            // enough; it actually needs to happen during the dragstart event.
            // https://bugs.chromium.org/p/chromium/issues/detail?id=1203107
            const overlay = quickActionsOverlayRef.current;
            if (overlay) {
                overlay.style.opacity = "0";
                setTimeout(() => (overlay.style.opacity = "1"), 0);
            }
        }, []);
        const dragSpec = { tabId, panelId: childId, onDragStart };
        const [connectOverlayDragSource, connectOverlayDragPreview] = usePanelDrag(dragSpec);
        const [connectToolbarDragHandle, connectToolbarDragPreview] = usePanelDrag(dragSpec);
        const panelOverlayProps = useMemo(() => {
            const overlayProps = {
                open: isDragging || quickActionsKeyPressed || (isSelected && numSelectedPanelsIfSelected > 1),
                variant: undefined,
                highlightMode: undefined,
                actions: undefined,
                dropMessage,
            };
            if (isDragging && !isValidTarget) {
                overlayProps.variant = "invalidDropTarget";
            }
            if (isDragging && isOver) {
                overlayProps.variant = "validDropTarget";
            }
            if (isSelected && numSelectedPanelsIfSelected > 1) {
                overlayProps.onClickAway = () => {
                    setSelectedPanelIds([]);
                };
                overlayProps.variant = "selected";
                overlayProps.highlightMode = "all";
                overlayProps.actions = [
                    {
                        key: "group",
                        text: "Group in tab",
                        icon: _jsx(TabDesktop20Regular, {}),
                        onClick: groupPanels,
                    },
                    {
                        key: "create-tabs",
                        text: "Create tabs",
                        icon: (_jsxs(_Fragment, { children: [_jsxs("span", { className: classes.tabCount, children: [numSelectedPanelsIfSelected <= 99 ? numSelectedPanelsIfSelected : "", " "] }), _jsx(TabDesktopMultiple20Regular, {})] })),
                        onClick: createTabs,
                    },
                ];
            }
            if (type !== TAB_PANEL_TYPE && quickActionsKeyPressed) {
                overlayProps.variant = "selected";
                overlayProps.highlightMode = "active";
            }
            if (quickActionsKeyPressed) {
                overlayProps.actions = [
                    {
                        key: "split",
                        text: "Split panel",
                        icon: _jsx(TableSimple20Regular, {}),
                        onClick: splitPanel,
                    },
                    {
                        key: "remove",
                        text: "Remove panel",
                        icon: _jsx(Delete20Regular, {}),
                        color: "error",
                        onClick: removePanel,
                    },
                ];
            }
            return overlayProps;
        }, [
            classes.tabCount,
            createTabs,
            dropMessage,
            groupPanels,
            isDragging,
            isOver,
            isSelected,
            isValidTarget,
            numSelectedPanelsIfSelected,
            quickActionsKeyPressed,
            removePanel,
            setSelectedPanelIds,
            splitPanel,
            type,
        ]);
        return (_jsx(Profiler, { id: childId, onRender: (_id, _phase, actualDuration, _baseDuration, _startTime, _commitTime, _interactions) => {
                if (perfInfo.current) {
                    perfInfo.current.innerText = `${++renderCount.current}\n${actualDuration.toFixed(1)}ms`;
                }
            }, children: _jsxs(PanelContext.Provider, { value: {
                    type,
                    id: childId,
                    title,
                    config: panelComponentConfig,
                    saveConfig: saveConfig,
                    updatePanelConfigs,
                    openSiblingPanel,
                    replacePanel,
                    enterFullscreen,
                    exitFullscreen,
                    setHasFullscreenDescendant,
                    isFullscreen: fullscreen,
                    tabId,
                    // disallow dragging the root panel in a layout
                    connectToolbarDragHandle: isTopLevelPanel ? undefined : connectToolbarDragHandle,
                    setMessagePathDropConfig,
                }, children: [_jsx(KeyListener, { global: true, keyUpHandlers: keyUpHandlers, keyDownHandlers: keyDownHandlers }), fullscreen && _jsx(KeyListener, { global: true, keyDownHandlers: fullScreenKeyHandlers }), _jsx(Transition, { in: fullscreen, onExited: () => {
                            setHasFullscreenDescendant(false);
                        }, nodeRef: panelRootRef, timeout: {
                            // match to transition duration inside PanelRoot
                            exit: theme.transitions.duration.shorter,
                        }, children: (fullscreenState) => (_jsxs(PanelRoot, { onClick: onPanelRootClick, hasFullscreenDescendant: hasFullscreenDescendant, fullscreenState: fullscreenState, sourceRect: fullscreenSourceRect, selected: isSelected || (isDragging && isValidTarget && isOver), "data-testid": cx("panel-mouseenter-container", childId), ref: (el) => {
                                panelRootRef.current = el;
                                // disallow dragging the root panel in a layout
                                if (!isTopLevelPanel) {
                                    connectOverlayDragPreview(el);
                                    connectToolbarDragPreview(el);
                                }
                                connectMessagePathDropTarget(el);
                            }, children: [!fullscreen && type !== TAB_PANEL_TYPE && (_jsx(PanelOverlay, { ...panelOverlayProps, ref: (el) => {
                                        quickActionsOverlayRef.current = el;
                                        // disallow dragging the root panel in a layout
                                        if (!isTopLevelPanel) {
                                            connectOverlayDragSource(el);
                                        }
                                    } })), _jsx(PanelErrorBoundary, { onRemovePanel: removePanel, onResetPanel: resetPanel, children: _jsx(React.StrictMode, { children: child }) }), process.env.NODE_ENV !== "production" && (_jsx("div", { className: classes.perfInfo, ref: perfInfo }))] })) })] }) }));
    }
    return Object.assign(React.memo(ConnectedPanel), {
        defaultConfig: PanelComponent.defaultConfig,
        panelType: PanelComponent.panelType,
        displayName: `Panel(${PanelComponent.displayName ?? PanelComponent.name})`,
    });
}
