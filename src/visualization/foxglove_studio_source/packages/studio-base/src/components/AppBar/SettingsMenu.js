import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { Divider, Menu, MenuItem, } from "@mui/material";
import { useCallback } from "react";
import { useTranslation } from "react-i18next";
import { makeStyles } from "tss-react/mui";
import { useAppContext } from "@foxglove/studio-base/context/AppContext";
import { useWorkspaceActions } from "@foxglove/studio-base/context/Workspace/useWorkspaceActions";
const useStyles = makeStyles()({
    menuList: {
        minWidth: 200,
    },
});
export function SettingsMenu({ anchorEl, anchorReference, anchorPosition, disablePortal, handleClose, open, }) {
    const { classes } = useStyles();
    const { t } = useTranslation("appBar");
    const { extensionSettings } = useAppContext();
    const { dialogActions } = useWorkspaceActions();
    const onSettingsClick = useCallback((tab) => {
        dialogActions.preferences.open(tab);
    }, [dialogActions.preferences]);
    const onDocsClick = useCallback(() => {
        window.open("https://docs.foxglove.dev/docs", "_blank");
    }, []);
    const onSlackClick = useCallback(() => {
        window.open("https://foxglove.dev/slack", "_blank");
    }, []);
    return (_jsx(_Fragment, { children: _jsxs(Menu, { anchorEl: anchorEl, anchorReference: anchorReference, anchorPosition: anchorPosition, disablePortal: disablePortal, id: "user-menu", open: open, onClose: handleClose, onClick: handleClose, MenuListProps: { className: classes.menuList, dense: true }, PaperProps: {
                "data-tourid": "user-menu",
            }, children: [_jsx(MenuItem, { onClick: () => {
                        onSettingsClick();
                    }, children: t("settings") }), extensionSettings && (_jsx(MenuItem, { onClick: () => {
                        onSettingsClick("extensions");
                    }, children: t("extensions") })), _jsx(Divider, { variant: "middle" }), _jsx(MenuItem, { onClick: onDocsClick, children: t("documentation") }), _jsx(MenuItem, { onClick: onSlackClick, children: t("joinSlackCommunity") })] }) }));
}
