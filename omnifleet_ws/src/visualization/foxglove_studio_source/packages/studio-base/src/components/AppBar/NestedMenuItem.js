import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { ChevronRight12Regular } from "@fluentui/react-icons";
import { Divider, Menu, MenuItem, Typography } from "@mui/material";
import { useState } from "react";
import { makeStyles } from "tss-react/mui";
const useStyles = makeStyles()((theme, _params, classes) => ({
    menu: {
        pointerEvents: "none",
    },
    paper: {
        pointerEvents: "auto",
        marginTop: theme.spacing(-1),
    },
    menuItem: {
        justifyContent: "space-between",
        cursor: "pointer",
        gap: theme.spacing(2),
        "&.Mui-selected, &.Mui-selected:hover": {
            backgroundColor: theme.palette.action.hover,
        },
        [`:not(:hover, :focus) .${classes.endIcon}`]: {
            opacity: 0.6,
        },
        kbd: {
            font: "inherit",
            color: theme.palette.text.disabled,
        },
    },
    menuList: {
        minWidth: 180,
        maxWidth: 280,
    },
    endIcon: {
        marginRight: theme.spacing(-0.75),
    },
}));
export function NestedMenuItem(props) {
    const { classes } = useStyles();
    const { children, items, open, onPointerEnter, id } = props;
    const [anchorEl, setAnchorEl] = useState(undefined);
    const handlePointerEnter = () => {
        if (id) {
            onPointerEnter(id);
        }
    };
    return (_jsxs(_Fragment, { children: [_jsxs(MenuItem, { id: id, ref: (element) => {
                    setAnchorEl(element ?? undefined);
                }, selected: open, className: classes.menuItem, onPointerEnter: handlePointerEnter, "data-testid": id, children: [children, _jsx(ChevronRight12Regular, { className: classes.endIcon })] }), _jsx(Menu, { classes: {
                    root: classes.menu,
                    paper: classes.paper,
                }, open: open, disablePortal: true, anchorEl: anchorEl, onClose: () => {
                    setAnchorEl(undefined);
                }, onMouseLeave: () => {
                    setAnchorEl(undefined);
                }, anchorOrigin: { vertical: "top", horizontal: "right" }, MenuListProps: { dense: true, className: classes.menuList }, autoFocus: false, disableAutoFocus: true, disableEnforceFocus: true, hideBackdrop: true, children: items.map((item, idx) => {
                    switch (item.type) {
                        case "item":
                            return (_jsxs(MenuItem, { className: classes.menuItem, onClick: item.onClick, disabled: item.disabled, children: [item.label, item.shortcut && _jsx("kbd", { children: item.shortcut })] }, item.key));
                        case "divider":
                            return _jsx(Divider, { variant: "middle" }, `divider${idx}`);
                        case "subheader":
                            return (_jsx(MenuItem, { disabled: true, children: _jsx(Typography, { variant: "overline", children: item.label }) }, item.key));
                    }
                }) })] }));
}
