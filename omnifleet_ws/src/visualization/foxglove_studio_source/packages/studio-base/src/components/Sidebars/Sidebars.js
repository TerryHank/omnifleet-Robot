import { jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { useCallback, useEffect, useMemo, useState } from "react";
import { MosaicWithoutDragDropContext } from "react-mosaic-component";
import { makeStyles } from "tss-react/mui";
import ErrorBoundary from "@foxglove/studio-base/components/ErrorBoundary";
import Stack from "@foxglove/studio-base/components/Stack";
import { Sidebar } from "./Sidebar";
import "react-mosaic-component/react-mosaic-component.css";
const useStyles = makeStyles()({
    mosaicWrapper: {
        flex: "1 1 100%",
        // Root drop targets in this top level sidebar mosaic interfere with drag/mouse events from the
        // PanelList. We don't allow users to edit the mosaic since it's just used for the sidebar, so we
        // can hide the drop targets.
        "& > .mosaic > .drop-target-container": {
            display: "none !important",
        },
    },
});
/**
 * Extract existing left split percentage from a layout node or return the default.
 */
function mosiacLeftSidebarSplitPercentage(node) {
    if (typeof node !== "object") {
        return undefined;
    }
    if (node.first === "leftbar") {
        return node.splitPercentage;
    }
    else {
        return (mosiacLeftSidebarSplitPercentage(node.first) ?? mosiacLeftSidebarSplitPercentage(node.second));
    }
}
/**
 * Extract existing right split percentage from a layout node or return the default.
 */
function mosiacRightSidebarSplitPercentage(node) {
    if (typeof node !== "object") {
        return undefined;
    }
    if (node.second === "rightbar") {
        return node.splitPercentage;
    }
    else {
        return (mosiacRightSidebarSplitPercentage(node.first) ??
            mosiacRightSidebarSplitPercentage(node.second));
    }
}
export function Sidebars(props) {
    const { children, leftItems, selectedLeftKey, onSelectLeftKey, leftSidebarSize, setLeftSidebarSize, rightItems, selectedRightKey, onSelectRightKey, rightSidebarSize, setRightSidebarSize, } = props;
    const [mosaicValue, setMosaicValue] = useState("children");
    const { classes } = useStyles();
    const leftSidebarOpen = selectedLeftKey != undefined;
    const rightSidebarOpen = selectedRightKey != undefined;
    // Select an available item if the selected one is not actually available
    useEffect(() => {
        if (leftSidebarOpen && !leftItems.has(selectedLeftKey)) {
            onSelectLeftKey([...leftItems.keys()][0]);
        }
        if (rightSidebarOpen && !rightItems.has(selectedRightKey)) {
            onSelectRightKey([...rightItems.keys()][0]);
        }
    }, [
        leftItems,
        leftSidebarOpen,
        onSelectLeftKey,
        onSelectRightKey,
        rightItems,
        rightSidebarOpen,
        selectedLeftKey,
        selectedRightKey,
    ]);
    useEffect(() => {
        const leftTargetWidth = 320;
        const rightTargetWidth = 320;
        const defaultLeftPercentage = 100 * (leftTargetWidth / window.innerWidth);
        const defaultRightPercentage = 100 * (1 - rightTargetWidth / window.innerWidth);
        setMosaicValue((oldValue) => {
            let node = "children";
            if (rightSidebarOpen) {
                node = {
                    direction: "row",
                    first: node,
                    second: "rightbar",
                    splitPercentage: rightSidebarSize ??
                        mosiacRightSidebarSplitPercentage(oldValue) ??
                        defaultRightPercentage,
                };
            }
            if (leftSidebarOpen) {
                node = {
                    direction: "row",
                    first: "leftbar",
                    second: node,
                    splitPercentage: leftSidebarSize ?? mosiacLeftSidebarSplitPercentage(oldValue) ?? defaultLeftPercentage,
                };
            }
            return node;
        });
    }, [leftSidebarSize, rightSidebarSize, leftSidebarOpen, rightSidebarOpen]);
    const onChangeMosaicValue = useCallback((newValue) => {
        if (newValue != undefined) {
            setMosaicValue(newValue);
            setLeftSidebarSize(mosiacLeftSidebarSplitPercentage(newValue));
            setRightSidebarSize(mosiacRightSidebarSplitPercentage(newValue));
        }
    }, [setLeftSidebarSize, setRightSidebarSize]);
    const childrenComponent = useMemo(() => _jsx(ErrorBoundary, { children: children }), [children]);
    const leftSidebarComponent = useMemo(() => (_jsx(ErrorBoundary, { children: _jsx(Sidebar, { anchor: "left", onClose: () => {
                onSelectLeftKey(undefined);
            }, items: leftItems, activeTab: selectedLeftKey, setActiveTab: onSelectLeftKey }) })), [leftItems, onSelectLeftKey, selectedLeftKey]);
    const rightSidebarComponent = useMemo(() => (_jsx(ErrorBoundary, { children: _jsx(Sidebar, { anchor: "right", onClose: () => {
                onSelectRightKey(undefined);
            }, items: rightItems, activeTab: selectedRightKey, setActiveTab: onSelectRightKey }) })), [onSelectRightKey, rightItems, selectedRightKey]);
    return (_jsx(Stack, { direction: "row", fullHeight: true, overflow: "hidden", children: _jsx("div", { className: classes.mosaicWrapper, children: _jsx(MosaicWithoutDragDropContext, { className: "", value: mosaicValue, onChange: onChangeMosaicValue, renderTile: (id) => {
                    switch (id) {
                        case "children":
                            return childrenComponent;
                        case "leftbar":
                            return leftSidebarComponent;
                        case "rightbar":
                            return rightSidebarComponent;
                    }
                }, resize: { minimumPaneSizePercentage: 10 } }) }) }));
}
