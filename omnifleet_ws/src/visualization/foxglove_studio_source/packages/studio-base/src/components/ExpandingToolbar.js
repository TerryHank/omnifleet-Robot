import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { ArrowMinimize20Filled } from "@fluentui/react-icons";
import { Paper, IconButton, Tabs, Tab, tabClasses, tabsClasses, Tooltip } from "@mui/material";
import { makeStyles } from "tss-react/mui";
import Stack from "@foxglove/studio-base/components/Stack";
const PANE_HEIGHT = 240;
const useStyles = makeStyles()((theme) => ({
    root: {
        pointerEvents: "auto",
        backgroundColor: theme.palette.background.default,
        width: 280,
    },
    content: {
        position: "relative",
    },
    tabs: {
        minHeight: "auto",
        [`.${tabsClasses.indicator}`]: {
            transform: "scaleX(0.75)",
            height: 2,
        },
        [`.${tabClasses.root}`]: {
            minWidth: "auto",
            minHeight: "auto",
            padding: theme.spacing(0.875, 1.5, 1),
            color: theme.palette.text.secondary,
            "&.Mui-selected": {
                color: theme.palette.text.primary,
            },
        },
    },
    minimizeButton: {
        borderRadius: 0,
        borderTopRightRadius: theme.shape.borderRadius,
    },
}));
export function ToolGroup({ children }) {
    return children;
}
export function ToolGroupFixedSizePane({ children }) {
    return (_jsx(Stack, { padding: 1, overflowX: "hidden", overflowY: "auto", style: { maxHeight: PANE_HEIGHT }, children: children }));
}
export default function ExpandingToolbar({ children, checked, icon, onSelectTab, selectedTab, tooltip, dataTest, }) {
    const { classes } = useStyles();
    const expanded = selectedTab != undefined;
    if (!expanded) {
        let selectedTabLocal = selectedTab;
        // default to the first child's name if no tab is selected
        React.Children.forEach(children, (child) => {
            if (selectedTabLocal == undefined) {
                selectedTabLocal = child.props.name;
            }
        });
        return (_jsx(Paper, { square: false, elevation: 4, style: { pointerEvents: "auto" }, children: _jsx(Tooltip, { placement: "left", title: tooltip, children: _jsx(IconButton, { size: "small", color: checked === true ? "info" : "default", "data-testid": `ExpandingToolbar-${tooltip}`, onClick: () => {
                        onSelectTab(selectedTabLocal);
                    }, children: icon }) }) }));
    }
    let selectedChild;
    React.Children.forEach(children, (child) => {
        if (!selectedChild || child.props.name === selectedTab) {
            selectedChild = child;
        }
    });
    const handleChange = (_event, value) => {
        if (value != undefined) {
            onSelectTab(value);
        }
    };
    return (_jsxs(Paper, { className: classes.root, "data-testid": dataTest, square: false, elevation: 4, children: [_jsx(Paper, { children: _jsxs(Stack, { direction: "row", justifyContent: "space-between", alignItems: "center", children: [_jsx(Tabs, { className: classes.tabs, textColor: "inherit", value: selectedTab, onChange: handleChange, children: React.Children.map(children, (child) => (_jsx(Tab, { label: child.props.name, value: child.props.name }))) }), _jsx(IconButton, { size: "small", className: classes.minimizeButton, onClick: () => {
                                onSelectTab(undefined);
                            }, children: _jsx(ArrowMinimize20Filled, {}) })] }) }), _jsx("div", { className: classes.content, children: selectedChild })] }));
}
