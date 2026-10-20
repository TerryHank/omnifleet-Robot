import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import MoreVertIcon from "@mui/icons-material/MoreVert";
import { Menu, MenuItem, IconButton, ListItemIcon, ListItemText, Divider } from "@mui/material";
import { useState } from "react";
import { icons } from "./icons";
export function NodeActionsMenu({ actions, onSelectAction, }) {
    const [anchorEl, setAnchorEl] = useState(undefined);
    const open = Boolean(anchorEl);
    const handleClick = (event) => {
        setAnchorEl(event.currentTarget);
    };
    const handleClose = (id) => {
        onSelectAction(id);
        setAnchorEl(undefined);
    };
    const anyItemHasIcon = actions.some((action) => action.type === "action" && action.icon);
    return (_jsxs(_Fragment, { children: [_jsx(IconButton, { title: "\u66F4\u591A\u64CD\u4F5C", "aria-controls": open ? "node-actions-menu" : undefined, "aria-haspopup": "true", "aria-expanded": open ? "true" : undefined, onClick: handleClick, "data-testid": "node-actions-menu-button", size: "small", children: _jsx(MoreVertIcon, { fontSize: "small" }) }), _jsx(Menu, { id: "basic-menu", anchorEl: anchorEl, open: open, onClose: () => {
                    setAnchorEl(undefined);
                }, MenuListProps: {
                    "aria-label": "node actions button",
                    dense: true,
                }, children: actions.map((action, index) => {
                    if (action.type === "divider") {
                        return (_jsx(Divider, { variant: anyItemHasIcon ? "inset" : "fullWidth" }, `divider_${index}`));
                    }
                    const Icon = action.icon ? icons[action.icon] : undefined;
                    return (_jsxs(MenuItem, { onClick: () => {
                            handleClose(action.id);
                        }, children: [Icon && (_jsx(ListItemIcon, { children: _jsx(Icon, { fontSize: "small" }) })), _jsx(ListItemText, { inset: !Icon && anyItemHasIcon, disableTypography: true, children: action.label })] }, action.id));
                }) })] }));
}
