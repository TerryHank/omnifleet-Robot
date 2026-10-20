import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { Ruler20Filled, Ruler20Regular } from "@fluentui/react-icons";
import { Button, IconButton, ListItemIcon, ListItemText, Menu, MenuItem, Paper, Tooltip, useTheme, } from "@mui/material";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { useLongPress } from "react-use";
import tc from "tinycolor2";
import { makeStyles } from "tss-react/mui";
import { PanelContextMenu, } from "@foxglove/studio-base/components/PanelContextMenu";
import PublishGoalIcon from "@foxglove/studio-base/components/PublishGoalIcon";
import PublishPointIcon from "@foxglove/studio-base/components/PublishPointIcon";
import PublishPoseEstimateIcon from "@foxglove/studio-base/components/PublishPoseEstimateIcon";
import { usePanelMousePresence } from "@foxglove/studio-base/hooks/usePanelMousePresence";
import { HUD } from "@foxglove/studio-base/panels/ThreeDeeRender/HUD";
import { InteractionContextMenu, Interactions } from "./Interactions";
import { useRenderer, useRendererEvent } from "./RendererContext";
import { Stats } from "./Stats";
const PublishClickIcons = {
    pose: _jsx(PublishGoalIcon, { fontSize: "small" }),
    point: _jsx(PublishPointIcon, { fontSize: "small" }),
    pose_estimate: _jsx(PublishPoseEstimateIcon, { fontSize: "small" }),
};
const useStyles = makeStyles()((theme) => ({
    root: {
        position: "absolute",
        top: 10,
        right: 10,
        display: "flex",
        flexDirection: "column",
        alignItems: "flex-end",
        gap: 10,
        pointerEvents: "none",
    },
    iconButton: {
        position: "relative",
        pointerEvents: "auto",
        aspectRatio: "1/1",
    },
    rulerIcon: {
        transform: "rotate(45deg)",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
    },
    threeDeeButton: {
        fontFamily: theme.typography.fontMonospace,
        fontFeatureSettings: theme.typography.caption.fontFeatureSettings,
        fontSize: theme.typography.caption.fontSize,
        fontWeight: theme.typography.fontWeightBold,
        lineHeight: "1em",
    },
    resetViewButton: {
        position: "absolute",
        bottom: 0,
        right: 0,
        marginBottom: theme.spacing(1),
        marginRight: theme.spacing(1),
    },
    kbd: {
        fontFamily: theme.typography.fontMonospace,
        background: tc(theme.palette.common.white).darken(45).toString(),
        padding: theme.spacing(0, 0.5),
        aspectRatio: 1,
        borderRadius: theme.shape.borderRadius,
        marginLeft: theme.spacing(1),
    },
}));
/**
 * Provides DOM overlay elements on top of the 3D scene (e.g. stats, debug GUI).
 */
export function RendererOverlay(props) {
    const { t } = useTranslation("threeDee");
    const { classes } = useStyles();
    const [clickedPosition, setClickedPosition] = useState({
        clientX: 0,
        clientY: 0,
    });
    const [selectedRenderables, setSelectedRenderables] = useState([]);
    const [selectedRenderable, setSelectedRenderable] = useState(undefined);
    const [interactionsTabType, setInteractionsTabType] = useState(undefined);
    const renderer = useRenderer();
    // Toggle object selection mode on/off in the renderer
    useEffect(() => {
        if (renderer) {
            renderer.setPickingEnabled(interactionsTabType != undefined);
        }
    }, [interactionsTabType, renderer]);
    useRendererEvent("renderablesClicked", (selections, cursorCoords) => {
        const rect = props.canvas.getBoundingClientRect();
        setClickedPosition({ clientX: rect.left + cursorCoords.x, clientY: rect.top + cursorCoords.y });
        setSelectedRenderables(selections);
        setSelectedRenderable(selections.length === 1 ? selections[0] : undefined);
    });
    const [showResetViewButton, setShowResetViewButton] = useState(renderer?.canResetView() ?? false);
    useRendererEvent("resetViewChanged", useCallback(() => {
        setShowResetViewButton(renderer?.canResetView() ?? false);
    }, [renderer]));
    const onResetView = useCallback(() => {
        renderer?.resetView();
    }, [renderer]);
    const stats = props.enableStats ? (_jsx("div", { id: "stats", style: { position: "absolute", top: "10px", left: "10px" }, children: _jsx(Stats, {}) })) : undefined;
    // Convert the list of selected renderables (if any) into MouseEventObjects
    // that can be passed to <InteractionContextMenu>, which shows a context menu
    // of candidate objects to select
    const clickedObjects = useMemo(() => selectedRenderables.map((selection) => ({
        object: {
            pose: selection.renderable.pose,
            scale: selection.renderable.scale,
            color: undefined,
            interactionData: {
                topic: selection.renderable.name,
                highlighted: undefined,
                renderable: selection.renderable,
            },
        },
        instanceIndex: selection.instanceIndex,
    })), [selectedRenderables]);
    // Once a single renderable is selected, convert it to the SelectionObject
    // format to populate the object inspection dialog (<Interactions>)
    const selectedObject = useMemo(() => selectedRenderable
        ? {
            object: {
                pose: selectedRenderable.renderable.pose,
                interactionData: {
                    topic: selectedRenderable.renderable.topic,
                    highlighted: true,
                    originalMessage: selectedRenderable.renderable.details(),
                    instanceDetails: selectedRenderable.instanceIndex != undefined
                        ? selectedRenderable.renderable.instanceDetails(selectedRenderable.instanceIndex)
                        : undefined,
                },
            },
            instanceIndex: selectedRenderable.instanceIndex,
        }
        : undefined, [selectedRenderable]);
    // Inform the Renderer when a renderable is selected
    useEffect(() => {
        renderer?.setSelectedRenderable(selectedRenderable);
    }, [renderer, selectedRenderable]);
    const publickClickButtonRef = useRef(ReactNull);
    const [publishMenuExpanded, setPublishMenuExpanded] = useState(false);
    const selectedPublishClickIcon = PublishClickIcons[props.publishClickType];
    const onLongPressPublish = useCallback(() => {
        setPublishMenuExpanded(true);
    }, []);
    const longPressPublishEvent = useLongPress(onLongPressPublish);
    const theme = useTheme();
    // Publish control is only available if the canPublish prop is true and we have a fixed frame in the renderer
    const showPublishControl = props.interfaceMode === "3d" && props.canPublish && renderer?.fixedFrameId != undefined;
    const publishControls = showPublishControl && (_jsxs(_Fragment, { children: [_jsx(Tooltip, { placement: "left", title: props.publishActive ? "Click to cancel" : "Click to publish", children: _jsxs(IconButton, { ...longPressPublishEvent, className: classes.iconButton, size: "small", color: props.publishActive ? "info" : "inherit", ref: publickClickButtonRef, onClick: props.onClickPublish, "data-testid": "publish-button", children: [selectedPublishClickIcon, _jsx("div", { style: {
                                borderBottom: "6px solid currentColor",
                                borderRight: "6px solid transparent",
                                bottom: 0,
                                left: 0,
                                height: 0,
                                width: 0,
                                margin: theme.spacing(0.25),
                                position: "absolute",
                            } })] }) }), _jsxs(Menu, { id: "publish-menu", anchorEl: publickClickButtonRef.current, anchorOrigin: { vertical: "top", horizontal: "left" }, transformOrigin: { vertical: "top", horizontal: "right" }, open: publishMenuExpanded, onClose: () => {
                    setPublishMenuExpanded(false);
                }, MenuListProps: { dense: true }, children: [_jsxs(MenuItem, { selected: props.publishClickType === "pose_estimate", onClick: () => {
                            props.onChangePublishClickType("pose_estimate");
                            setPublishMenuExpanded(false);
                        }, children: [_jsx(ListItemIcon, { children: PublishClickIcons.pose_estimate }), _jsx(ListItemText, { disableTypography: true, children: "Publish pose estimate" })] }), _jsxs(MenuItem, { selected: props.publishClickType === "pose", onClick: () => {
                            props.onChangePublishClickType("pose");
                            setPublishMenuExpanded(false);
                        }, children: [_jsx(ListItemIcon, { children: PublishClickIcons.pose }), _jsx(ListItemText, { disableTypography: true, children: "Publish pose" })] }), _jsxs(MenuItem, { selected: props.publishClickType === "point", onClick: () => {
                            props.onChangePublishClickType("point");
                            setPublishMenuExpanded(false);
                        }, children: [_jsx(ListItemIcon, { children: PublishClickIcons.point }), _jsx(ListItemText, { disableTypography: true, children: "Publish point" })] })] })] }));
    const resetViewButton = showResetViewButton && (_jsx(Button, { className: classes.resetViewButton, variant: "contained", color: "secondary", onClick: onResetView, "data-testid": "reset-view", children: t("resetView") }));
    const getContextMenuItems = useCallback(() => {
        return renderer?.getContextMenuItems() ?? [];
    }, [renderer]);
    const mousePresenceRef = useRef(ReactNull);
    const mousePresent = usePanelMousePresence(mousePresenceRef);
    return (_jsxs(_Fragment, { children: [props.interfaceMode === "image" && _jsx(PanelContextMenu, { getItems: getContextMenuItems }), _jsxs("div", { ref: mousePresenceRef, className: classes.root, children: [
                    // Only show on hover for image panel
                    (props.interfaceMode === "3d" || mousePresent) && (_jsx(Interactions, { addPanel: props.addPanel, interactionsTabType: interactionsTabType, onShowTopicSettings: props.onShowTopicSettings, selectedObject: selectedObject, setInteractionsTabType: setInteractionsTabType, timezone: props.timezone })), props.interfaceMode === "3d" && (_jsxs(Paper, { square: false, elevation: 4, style: { display: "flex", flexDirection: "column" }, children: [_jsx(Tooltip, { placement: "left", title: _jsxs(_Fragment, { children: [`Switch to ${props.perspective ? "2" : "3"}D camera `, _jsx("kbd", { className: classes.kbd, children: "3" })] }), children: _jsx(IconButton, { className: classes.iconButton, size: "small", color: props.perspective ? "info" : "inherit", onClick: props.onTogglePerspective, children: _jsx("span", { className: classes.threeDeeButton, children: "3D" }) }) }), _jsx(Tooltip, { placement: "left", title: props.measureActive ? "Cancel measuring" : "Measure distance", children: _jsx(IconButton, { "data-testid": "measure-button", className: classes.iconButton, size: "small", color: props.measureActive ? "info" : "inherit", onClick: props.onClickMeasure, children: _jsx("div", { className: classes.rulerIcon, children: props.measureActive ? _jsx(Ruler20Filled, {}) : _jsx(Ruler20Regular, {}) }) }) }), publishControls] }))] }), clickedObjects.length > 1 && !selectedObject && (_jsx(InteractionContextMenu, { onClose: () => {
                    setSelectedRenderables([]);
                }, clickedPosition: clickedPosition, clickedObjects: clickedObjects, selectObject: (selection) => {
                    if (selection) {
                        const renderable = selection.object.interactionData.renderable;
                        const instanceIndex = selection.instanceIndex;
                        setSelectedRenderables([]);
                        setSelectedRenderable({ renderable, instanceIndex });
                    }
                } })), _jsx(HUD, { renderer: renderer }), stats, resetViewButton] }));
}
