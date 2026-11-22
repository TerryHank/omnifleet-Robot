import { jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { Menu } from "@mui/material";
import { makeStyles } from "tss-react/mui";
import { PanelCatalog } from "@foxglove/studio-base/components/PanelCatalog";
import useAddPanel from "@foxglove/studio-base/hooks/useAddPanel";
const useStyles = makeStyles()((theme) => ({
    menuList: {
        minWidth: 270,
        paddingBottom: theme.spacing(1),
    },
}));
export function AddPanelMenu(props) {
    const { classes } = useStyles();
    const { anchorEl, anchorPosition, anchorReference, disablePortal, handleClose, open } = props;
    const addPanel = useAddPanel();
    return (_jsx(Menu, { id: "add-panel-menu", anchorEl: anchorEl, anchorPosition: anchorPosition, anchorReference: anchorReference, disablePortal: disablePortal, open: open, onClose: handleClose, MenuListProps: {
            dense: true,
            disablePadding: true,
            "aria-labelledby": "add-panel-button",
            className: classes.menuList,
        }, anchorOrigin: {
            horizontal: "left",
            vertical: "bottom",
        }, transformOrigin: {
            vertical: "top",
            horizontal: "left",
        }, PaperProps: {
            "data-tourid": "add-panel-menu",
        }, children: _jsx(PanelCatalog, { isMenu: true, 
            // Close when a drag starts so the modal menu doesn't block the drop targets
            onDragStart: handleClose, onPanelSelect: (selection) => {
                addPanel(selection);
                handleClose();
            } }) }));
}
