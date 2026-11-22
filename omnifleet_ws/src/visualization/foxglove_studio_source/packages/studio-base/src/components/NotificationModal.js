import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import CloseIcon from "@mui/icons-material/Close";
import { Dialog, DialogTitle, IconButton, Typography } from "@mui/material";
import { useMemo } from "react";
import { makeStyles } from "tss-react/mui";
const useStyles = makeStyles()((theme) => ({
    container: {
        alignItems: "stretch",
        display: "flex",
        flexDirection: "column",
        maxHeight: "50vw",
        marginBlockEnd: theme.spacing(3),
        marginInline: theme.spacing(3),
    },
    paper: {
        maxWidth: 700,
        width: "70%",
    },
    text: {
        backgroundColor: theme.palette.background.default,
        color: theme.palette.text.primary,
        fontSize: theme.typography.body1.fontSize,
        flex: 1,
        padding: theme.spacing(1),
        overflowY: "auto",
        whiteSpace: "pre-wrap",
    },
    iconButton: {
        position: "absolute",
        right: theme.spacing(1),
        top: theme.spacing(1),
    },
}));
export default function NotificationModal({ notification: { details, message, severity, subText }, onRequestClose, }) {
    const { classes, theme } = useStyles();
    const displayPropsBySeverity = {
        error: theme.palette.error.main,
        warn: theme.palette.warning.main,
        info: theme.palette.info.main,
    };
    const detailsElement = useMemo(() => {
        if (details instanceof Error) {
            return _jsx("div", { className: classes.text, children: details.stack });
        }
        else if (details != undefined && details !== "") {
            return (_jsx(Typography, { style: { whiteSpace: "pre-line" /* allow newlines in the details message */ }, children: details }));
        }
        else if (subText) {
            return undefined;
        }
        return "No details provided";
    }, [classes, details, subText]);
    return (_jsxs(Dialog, { classes: { paper: classes.paper }, fullWidth: true, open: true, onClose: () => onRequestClose?.(), children: [_jsx(DialogTitle, { color: displayPropsBySeverity[severity], children: message }), _jsxs("div", { className: classes.container, children: [subText && _jsx(Typography, { mb: 3, children: subText }), detailsElement] }), _jsx(IconButton, { "aria-label": "close", onClick: () => onRequestClose?.(), className: classes.iconButton, children: _jsx(CloseIcon, {}) })] }));
}
