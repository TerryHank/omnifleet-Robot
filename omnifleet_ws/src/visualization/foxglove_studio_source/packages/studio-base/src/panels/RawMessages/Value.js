import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import CheckIcon from "@mui/icons-material/Check";
import CopyAllIcon from "@mui/icons-material/CopyAll";
import ErrorIcon from "@mui/icons-material/Error";
import FilterIcon from "@mui/icons-material/FilterAlt";
import StateTransitionsIcon from "@mui/icons-material/PowerInput";
import ScatterPlotIcon from "@mui/icons-material/ScatterPlot";
import LineChartIcon from "@mui/icons-material/ShowChart";
import { Tooltip } from "@mui/material";
import { useCallback, useMemo, useState, useRef, useEffect } from "react";
import { withStyles, makeStyles } from "tss-react/mui";
import HoverableIconButton from "@foxglove/studio-base/components/HoverableIconButton";
import Stack from "@foxglove/studio-base/components/Stack";
import { openSiblingPlotPanel } from "@foxglove/studio-base/panels/Plot/openSiblingPlotPanel";
import { plotableRosTypes } from "@foxglove/studio-base/panels/Plot/plotableRosTypes";
import { openSiblingStateTransitionsPanel, transitionableRosTypes, } from "@foxglove/studio-base/panels/StateTransitions/openSiblingStateTransitionsPanel";
import clipboard from "@foxglove/studio-base/util/clipboard";
import HighlightedValue from "./HighlightedValue";
import { copyMessageReplacer } from "./copyMessageReplacer";
const StyledIconButton = withStyles(HoverableIconButton, (theme) => ({
    root: {
        "&.MuiIconButton-root": {
            fontSize: theme.typography.pxToRem(16),
            opacity: 0.6,
            padding: 0,
        },
    },
}));
const useStyles = makeStyles()({
    // always hidden, just used to keep space and prevent resizing on hover
    placeholderActionContainer: {
        alignItems: "inherit",
        display: "inherit",
        gap: "inherit",
        visibility: "hidden",
    },
});
const emptyAction = {
    key: "",
    tooltip: "",
    icon: _jsx(ErrorIcon, { fontSize: "inherit" }),
};
const MAX_ACTION_ITEMS = 4;
function Value(props) {
    const timeOutID = useRef(undefined);
    const { arrLabel, basePath, itemLabel, itemValue, valueAction, onTopicPathChange, openSiblingPanel, } = props;
    const [copied, setCopied] = useState(false);
    const openPlotPanel = useCallback((pathSuffix) => () => {
        openSiblingPlotPanel(openSiblingPanel, `${basePath}${pathSuffix}`);
    }, [basePath, openSiblingPanel]);
    const openStateTransitionsPanel = useCallback((pathSuffix) => () => {
        openSiblingStateTransitionsPanel(openSiblingPanel, `${basePath}${pathSuffix}`);
    }, [basePath, openSiblingPanel]);
    const onFilter = useCallback(() => {
        onTopicPathChange(`${basePath}${valueAction?.filterPath}`);
    }, [basePath, valueAction, onTopicPathChange]);
    const handleCopy = useCallback((value) => {
        clipboard
            .copy(value)
            .then(() => {
            setCopied(true);
            timeOutID.current = setTimeout(() => {
                setCopied(false);
            }, 1500);
        })
            .catch((e) => {
            console.warn(e);
        });
    }, []);
    const availableActions = useMemo(() => {
        const actions = [];
        if (arrLabel.length > 0) {
            actions.push({
                key: "Copy",
                activeColor: copied ? "success" : "primary",
                tooltip: copied ? "Copied" : "Copy to Clipboard",
                icon: copied ? _jsx(CheckIcon, { fontSize: "inherit" }) : _jsx(CopyAllIcon, { fontSize: "inherit" }),
                onClick: () => {
                    handleCopy(JSON.stringify(itemValue, copyMessageReplacer, 2) ?? "");
                },
            });
        }
        if (valueAction != undefined) {
            const isPlotableType = plotableRosTypes.includes(valueAction.primitiveType);
            const isTransitionalType = transitionableRosTypes.includes(valueAction.primitiveType);
            const isMultiSlicePath = valueAction.multiSlicePath === valueAction.singleSlicePath;
            if (valueAction.filterPath.length > 0) {
                actions.push({
                    key: "Filter",
                    tooltip: "按此值筛选",
                    icon: _jsx(FilterIcon, { fontSize: "inherit" }),
                    onClick: onFilter,
                });
            }
            if (isPlotableType) {
                actions.push({
                    key: "line",
                    tooltip: "在折线图中绘制此值",
                    icon: _jsx(LineChartIcon, { fontSize: "inherit" }),
                    onClick: openPlotPanel(valueAction.singleSlicePath),
                });
            }
            if (isPlotableType && !isMultiSlicePath) {
                actions.push({
                    key: "scatter",
                    tooltip: "在散点图中绘制此值",
                    icon: _jsx(ScatterPlotIcon, { fontSize: "inherit" }),
                    onClick: openPlotPanel(valueAction.multiSlicePath),
                });
            }
            if (isTransitionalType && isMultiSlicePath) {
                actions.push({
                    key: "stateTransitions",
                    tooltip: "查看此值的状态转换",
                    icon: _jsx(StateTransitionsIcon, { fontSize: "inherit" }),
                    onClick: openStateTransitionsPanel(valueAction.singleSlicePath),
                });
            }
        }
        return actions;
    }, [
        arrLabel.length,
        copied,
        handleCopy,
        itemValue,
        onFilter,
        openPlotPanel,
        openStateTransitionsPanel,
        valueAction,
    ]);
    // need to keep space to prevent resizing and wrapping on hover
    const placeholderActionsForSpacing = useMemo(() => {
        const actions = [];
        for (let i = availableActions.length; i < MAX_ACTION_ITEMS; i++) {
            actions.push({ ...emptyAction, key: `empty-${i}` });
        }
        return actions;
    }, [availableActions.length]);
    const { classes, cx } = useStyles();
    useEffect(() => {
        return () => {
            if (timeOutID.current != undefined) {
                clearTimeout(timeOutID.current);
            }
        };
    }, []);
    // The Tooltip and StyledIconButton components seem to be expensive to render so we
    // track our hover state and render them conditionally only when this component is
    // hovered.
    const [pointerOver, setPointerOver] = useState(false);
    return (_jsxs(Stack, { inline: true, flexWrap: "wrap", direction: "row", alignItems: "center", gap: 0.25, onPointerEnter: () => {
            setPointerOver(true);
        }, onPointerLeave: () => {
            setPointerOver(false);
        }, children: [_jsx(HighlightedValue, { itemLabel: itemLabel }), arrLabel, pointerOver &&
                availableActions.map((action) => (_jsx(Tooltip, { arrow: true, title: action.tooltip, placement: "top", children: _jsx(StyledIconButton, { size: "small", activeColor: action.activeColor, onClick: action.onClick, color: "inherit", icon: action.icon }) }, action.key))), _jsx("span", { className: cx(classes.placeholderActionContainer), children: pointerOver &&
                    placeholderActionsForSpacing.map((action) => (_jsx(Tooltip, { arrow: true, title: action.tooltip, placement: "top", children: _jsx(StyledIconButton, { size: "small", color: "inherit", icon: action.icon }) }, action.key))) })] }));
}
// In practice this seems to be an expensive component to render.
// Memoization provides a very noticeable performance boost.
export default React.memo(Value);
