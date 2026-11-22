import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import CloseIcon from "@mui/icons-material/Close";
import { Badge, Divider, IconButton, Tab, Tabs } from "@mui/material";
import { makeStyles } from "tss-react/mui";
import Stack from "@foxglove/studio-base/components/Stack";
const useStyles = makeStyles()((theme) => ({
    root: {
        boxSizing: "content-box",
        backgroundColor: theme.palette.background.paper,
    },
    badgeRoot: {
        display: "flex",
        alignItems: "baseline",
        gap: theme.spacing(1),
    },
    badge: {
        fontSize: theme.typography.caption.fontSize,
        padding: theme.spacing(0.125, 0.75),
        borderRadius: 8,
        transform: "none",
        position: "relative",
    },
    badgeInvisible: {
        display: "none",
    },
    anchorRight: {
        borderLeft: `1px solid ${theme.palette.divider}`,
    },
    anchorLeft: {
        borderRight: `1px solid ${theme.palette.divider}`,
    },
    tabs: {
        minHeight: "auto",
        flex: "1 1 auto",
        overflow: "hidden",
        paddingLeft: theme.spacing(0.25),
        ".MuiTabs-indicator": {
            transform: "scaleX(0.5)",
            height: 2,
        },
        ".MuiTab-root": {
            minHeight: 30,
            minWidth: theme.spacing(4),
            padding: theme.spacing(0, 1),
            color: theme.palette.text.secondary,
            fontSize: "0.6875rem",
            "&.Mui-selected": {
                color: theme.palette.text.primary,
            },
        },
    },
    iconButton: {
        padding: theme.spacing(0.91125), // round out the overall height to 30px
        color: theme.palette.text.secondary,
        borderRadius: 0,
        ":hover": {
            color: theme.palette.text.primary,
        },
    },
    tabContent: {
        flex: "auto",
        overflow: "auto",
    },
}));
function Noop() {
    return ReactNull;
}
export function Sidebar({ items, anchor, onClose, activeTab, setActiveTab, }) {
    const { classes, cx } = useStyles();
    const SelectedComponent = (activeTab && items.get(activeTab)?.component) ?? Noop;
    return (_jsxs(Stack, { className: cx(classes.root, {
            [classes.anchorLeft]: anchor === "left",
            [classes.anchorRight]: anchor === "right",
        }), flexShrink: 0, overflow: "hidden", "data-tourid": `sidebar-${anchor}`, children: [_jsxs(Stack, { direction: "row", justifyContent: "space-between", alignItems: "center", children: [_jsx(Tabs, { className: classes.tabs, textColor: "inherit", value: activeTab ?? false, onChange: (_ev, newValue) => {
                            if (newValue !== activeTab) {
                                setActiveTab(newValue);
                            }
                        }, children: Array.from(items.entries(), ([key, item]) => (_jsx(Tab, { label: _jsx(Badge, { invisible: item.badge == undefined, badgeContent: item.badge?.count, color: item.badge?.color, classes: {
                                    root: classes.badgeRoot,
                                    badge: classes.badge,
                                    invisible: classes.badgeInvisible,
                                }, children: item.title }), value: key, "data-testid": `${key}-${anchor}` }, key))) }), _jsx(IconButton, { className: classes.iconButton, onClick: onClose, size: "small", "data-testid": `sidebar-close-${anchor}`, children: _jsx(CloseIcon, { fontSize: "inherit" }) })] }), _jsx(Divider, {}), activeTab != undefined && (_jsx("div", { className: classes.tabContent, children: _jsx(SelectedComponent, {}) }))] }));
}
