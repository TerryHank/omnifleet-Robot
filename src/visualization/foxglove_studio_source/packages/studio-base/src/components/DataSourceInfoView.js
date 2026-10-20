import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { Skeleton, Typography } from "@mui/material";
import { useEffect, useRef } from "react";
import { useTranslation } from "react-i18next";
import { makeStyles } from "tss-react/mui";
import { subtract as subtractTimes } from "@foxglove/rostime";
import { useMessagePipeline, } from "@foxglove/studio-base/components/MessagePipeline";
import Stack from "@foxglove/studio-base/components/Stack";
import Timestamp from "@foxglove/studio-base/components/Timestamp";
import { useAppTimeFormat } from "@foxglove/studio-base/hooks";
import { PlayerPresence } from "@foxglove/studio-base/players/types";
import { formatDuration } from "@foxglove/studio-base/util/formatTime";
import { formatTimeRaw, isAbsoluteTime } from "@foxglove/studio-base/util/time";
import { MultilineMiddleTruncate } from "./MultilineMiddleTruncate";
const useStyles = makeStyles()((theme) => ({
    overline: {
        opacity: 0.6,
    },
    numericValue: {
        fontFeatureSettings: `${theme.typography.fontFeatureSettings}, "zero"`,
    },
}));
const selectStartTime = (ctx) => ctx.playerState.activeData?.startTime;
const selectEndTime = (ctx) => ctx.playerState.activeData?.endTime;
const selectPlayerName = (ctx) => ctx.playerState.name;
const selectPlayerPresence = ({ playerState }) => playerState.presence;
const selectSeek = (ctx) => ctx.seekPlayback;
function DataSourceInfoContent(props) {
    const { disableSource = false, durationRef, endTimeRef, playerName, playerPresence, startTime, } = props;
    const { classes } = useStyles();
    const { t } = useTranslation("dataSourceInfo");
    const isLiveConnection = props.isLiveConnection;
    return (_jsxs(Stack, { gap: 1.5, children: [!disableSource && (_jsxs(Stack, { children: [_jsx(Typography, { className: classes.overline, display: "block", variant: "overline", children: t("currentSource") }), playerPresence === PlayerPresence.INITIALIZING ? (_jsx(Typography, { variant: "inherit", children: _jsx(Skeleton, { animation: "wave", width: "40%" }) })) : playerPresence === PlayerPresence.RECONNECTING ? (_jsx(Typography, { variant: "inherit", children: t("waitingForConnection") })) : playerName ? (_jsx(Typography, { variant: "inherit", component: "span", children: _jsx(MultilineMiddleTruncate, { text: playerName }) })) : (_jsx(Typography, { className: classes.numericValue, variant: "inherit", children: "\u2014" }))] })), _jsxs(Stack, { children: [_jsx(Typography, { className: classes.overline, variant: "overline", children: t("startTime") }), playerPresence === PlayerPresence.INITIALIZING ? (_jsx(Skeleton, { animation: "wave", width: "50%" })) : startTime ? (_jsx(Timestamp, { horizontal: true, time: startTime })) : (_jsx(Typography, { className: classes.numericValue, variant: "inherit", children: "\u2014" }))] }), !isLiveConnection && (_jsxs(Stack, { children: [_jsx(Typography, { className: classes.overline, variant: "overline", children: t("endTime") }), playerPresence === PlayerPresence.INITIALIZING ? (_jsx(Skeleton, { animation: "wave", width: "50%" })) : (_jsx(Typography, { className: classes.numericValue, variant: "inherit", ref: endTimeRef, children: "\u2014" }))] })), _jsxs(Stack, { children: [_jsx(Typography, { className: classes.overline, variant: "overline", children: t("duration") }), playerPresence === PlayerPresence.INITIALIZING ? (_jsx(Skeleton, { animation: "wave", width: 100 })) : (_jsx(Typography, { className: classes.numericValue, variant: "inherit", ref: durationRef, children: "\u2014" }))] })] }));
}
const MemoDataSourceInfoContent = React.memo(DataSourceInfoContent);
const EmDash = "\u2014";
export function DataSourceInfoView({ disableSource }) {
    const startTime = useMessagePipeline(selectStartTime);
    const endTime = useMessagePipeline(selectEndTime);
    const playerName = useMessagePipeline(selectPlayerName);
    const playerPresence = useMessagePipeline(selectPlayerPresence);
    const seek = useMessagePipeline(selectSeek);
    const durationRef = useRef(ReactNull);
    const endTimeRef = useRef(ReactNull);
    const { formatDate, formatTime } = useAppTimeFormat();
    // We bypass react and update the DOM elements directly for better performance here.
    useEffect(() => {
        if (durationRef.current) {
            const duration = endTime && startTime ? subtractTimes(endTime, startTime) : undefined;
            if (duration) {
                const durationStr = formatDuration(duration);
                durationRef.current.innerText = durationStr;
            }
            else {
                durationRef.current.innerText = EmDash;
            }
        }
        if (endTimeRef.current) {
            if (endTime) {
                const date = formatDate(endTime);
                endTimeRef.current.innerText = !isAbsoluteTime(endTime)
                    ? `${formatTimeRaw(endTime)}`
                    : `${date} ${formatTime(endTime)}`;
            }
            else {
                endTimeRef.current.innerHTML = EmDash;
            }
        }
    }, [endTime, formatTime, startTime, playerPresence, formatDate]);
    return (_jsx(MemoDataSourceInfoContent, { disableSource: disableSource, durationRef: durationRef, endTimeRef: endTimeRef, playerName: playerName, playerPresence: playerPresence, startTime: startTime, isLiveConnection: seek == undefined }));
}
