import { Fragment as _Fragment, jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import CloseIcon from "@mui/icons-material/Close";
import { Dialog, DialogContent, DialogTitle, IconButton, Stack, Typography } from "@mui/material";
import { useState } from "react";
import { makeStyles } from "tss-react/mui";
import WssErrorModalScreenshot from "./WssErrorModal.png";
const useStyles = makeStyles()({
    image: {
        maxWidth: "24rem",
    },
    dialogTitle: {
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
    },
});
export default function WssErrorModal(props) {
    const { playerProblems } = props;
    const { classes } = useStyles();
    const [open, setOpen] = useState(true);
    const [hasDismissedWssErrorModal, setHasDismissedWssErrorModal] = useState(false);
    const handleClose = () => {
        setOpen(false);
        setHasDismissedWssErrorModal(true);
    };
    const hasWssConnectionProblem = playerProblems?.find((problem) => problem.severity === "error" && problem.message === "Insecure WebSocket connection");
    if (hasDismissedWssErrorModal || !hasWssConnectionProblem) {
        return _jsx(_Fragment, {});
    }
    return (_jsxs(Dialog, { open: open, onClose: handleClose, children: [_jsxs(DialogTitle, { className: classes.dialogTitle, children: ["WebSocket SSL Error", _jsx(IconButton, { onClick: () => {
                            setOpen(false);
                        }, edge: "end", children: _jsx(CloseIcon, {}) })] }), _jsx(DialogContent, { children: _jsxs(Stack, { gap: 2, children: [_jsxs(Typography, { variant: "body1", color: "text.secondary", children: ["By default, Chrome prevents a secure ", _jsx("code", { children: "https://" }), " page from connecting to an insecure ", _jsx("code", { children: "ws://" }), " WebSocket server. To allow the connection, enable \"Unsafe Scripts\" for this page."] }), _jsx(Typography, { variant: "body1", color: "text.secondary", children: "Click the shield icon at the end of your address bar, and then click \"Load Unsafe Scripts.\"" }), _jsx("img", { src: WssErrorModalScreenshot, alt: "WSS screenshot", className: classes.image })] }) })] }));
}
