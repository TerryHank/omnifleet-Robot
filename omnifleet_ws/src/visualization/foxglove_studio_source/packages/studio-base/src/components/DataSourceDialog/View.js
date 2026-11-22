import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import { Button } from "@mui/material";
import { makeStyles } from "tss-react/mui";
import Stack from "@foxglove/studio-base/components/Stack";
import { useWorkspaceActions } from "@foxglove/studio-base/context/Workspace/useWorkspaceActions";
const useStyles = makeStyles()((theme) => ({
    content: {
        display: "flex",
        flexDirection: "column",
        flexGrow: 1,
        height: "100%",
        justifyContent: "space-between",
        gap: theme.spacing(2),
        overflowY: "auto",
    },
}));
export default function View(props) {
    const { onOpen } = props;
    const { classes } = useStyles();
    const { dialogActions } = useWorkspaceActions();
    return (_jsxs(_Fragment, { children: [_jsx("div", { className: classes.content, children: props.children }), _jsxs(Stack, { direction: "row", justifyContent: "space-between", alignItems: "center", paddingX: 4, paddingBottom: 4, paddingTop: 2, children: [_jsx(Button, { startIcon: _jsx(ChevronLeftIcon, { fontSize: "large" }), onClick: () => {
                            dialogActions.dataSource.open("start");
                        }, children: "Back" }), _jsxs(Stack, { direction: "row", gap: 2, children: [_jsx(Button, { color: "inherit", variant: "outlined", onClick: () => {
                                    dialogActions.dataSource.close();
                                }, children: "Cancel" }), _jsx(Button, { variant: "contained", onClick: onOpen, disabled: onOpen == undefined, children: "Open" })] })] })] }));
    return _jsx(_Fragment, { children: props.children });
}
