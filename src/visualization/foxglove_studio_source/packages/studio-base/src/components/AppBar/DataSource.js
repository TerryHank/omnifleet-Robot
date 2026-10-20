import { jsx as _jsx, Fragment as _Fragment, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { ErrorCircle16Filled } from "@fluentui/react-icons";
import { CircularProgress, IconButton } from "@mui/material";
import { useTranslation } from "react-i18next";
import { makeStyles } from "tss-react/mui";
import { useMessagePipeline, } from "@foxglove/studio-base/components/MessagePipeline";
import Stack from "@foxglove/studio-base/components/Stack";
import TextMiddleTruncate from "@foxglove/studio-base/components/TextMiddleTruncate";
import WssErrorModal from "@foxglove/studio-base/components/WssErrorModal";
import { useWorkspaceActions } from "@foxglove/studio-base/context/Workspace/useWorkspaceActions";
import { PlayerPresence } from "@foxglove/studio-base/players/types";
import { EndTimestamp } from "./EndTimestamp";
const ICON_SIZE = 18;
const useStyles = makeStyles()((theme, _params, _classes) => ({
    sourceName: {
        font: "inherit",
        fontSize: theme.typography.body2.fontSize,
        display: "flex",
        alignItems: "center",
        gap: theme.spacing(0.5),
        padding: theme.spacing(1.5),
        paddingInlineEnd: theme.spacing(0.75),
        whiteSpace: "nowrap",
        minWidth: 0,
    },
    adornment: {
        display: "flex",
        flex: "none",
        alignItems: "center",
        justifyContent: "center",
        position: "relative",
        color: theme.palette.appBar.primary,
        width: ICON_SIZE,
        height: ICON_SIZE,
    },
    adornmentError: {
        color: theme.palette.error.main,
    },
    spinner: {
        position: "absolute",
        top: 0,
        right: 0,
        left: 0,
        bottom: 0,
        margin: "auto",
    },
    textTruncate: {
        maxWidth: "30vw",
        overflow: "hidden",
    },
    iconButton: {
        padding: 0,
        position: "relative",
        zIndex: 1,
        fontSize: ICON_SIZE - 2,
        "svg:not(.MuiSvgIcon-root)": {
            fontSize: "1rem",
        },
    },
}));
const selectPlayerName = (ctx) => ctx.playerState.name;
const selectPlayerPresence = (ctx) => ctx.playerState.presence;
const selectPlayerProblems = (ctx) => ctx.playerState.problems;
const selectSeek = (ctx) => ctx.seekPlayback;
export function DataSource() {
    const { t } = useTranslation("appBar");
    const { classes, cx } = useStyles();
    const playerName = useMessagePipeline(selectPlayerName);
    const playerPresence = useMessagePipeline(selectPlayerPresence);
    const playerProblems = useMessagePipeline(selectPlayerProblems) ?? [];
    const seek = useMessagePipeline(selectSeek);
    const { sidebarActions } = useWorkspaceActions();
    // A crude but correct proxy (for our current architecture) for whether a connection is live
    const isLiveConnection = seek == undefined;
    const reconnecting = playerPresence === PlayerPresence.RECONNECTING;
    const initializing = playerPresence === PlayerPresence.INITIALIZING;
    const error = playerPresence === PlayerPresence.ERROR ||
        playerProblems.some((problem) => problem.severity === "error");
    const loading = reconnecting || initializing;
    const playerDisplayName = initializing && playerName == undefined ? "Initializing…" : playerName;
    if (playerPresence === PlayerPresence.NOT_PRESENT) {
        return _jsx("div", { className: classes.sourceName, children: t("noDataSource") });
    }
    return (_jsxs(_Fragment, { children: [_jsx(WssErrorModal, { playerProblems: playerProblems }), _jsxs(Stack, { direction: "row", alignItems: "center", children: [_jsxs("div", { className: classes.sourceName, children: [_jsx("div", { className: classes.textTruncate, children: _jsx(TextMiddleTruncate, { text: playerDisplayName ?? `<${t("unknown")}>` }) }), isLiveConnection && (_jsxs(_Fragment, { children: [_jsx("span", { children: "/" }), _jsx(EndTimestamp, {})] }))] }), _jsxs("div", { className: cx(classes.adornment, { [classes.adornmentError]: error }), children: [loading && (_jsx(CircularProgress, { size: ICON_SIZE, color: "inherit", className: classes.spinner, variant: "indeterminate" })), error && (_jsx(IconButton, { color: "inherit", className: classes.iconButton, onClick: () => {
                                    sidebarActions.left.setOpen(true);
                                    sidebarActions.left.selectItem("problems");
                                }, children: _jsx(ErrorCircle16Filled, {}) }))] })] })] }));
}
