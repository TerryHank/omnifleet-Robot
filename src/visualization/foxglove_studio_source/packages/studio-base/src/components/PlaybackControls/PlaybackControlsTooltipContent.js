import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { Divider, Typography } from "@mui/material";
import * as _ from "lodash-es";
import { Fragment } from "react";
import { makeStyles } from "tss-react/mui";
import { subtract as subtractTimes, toSec } from "@foxglove/rostime";
import { useMessagePipeline, } from "@foxglove/studio-base/components/MessagePipeline";
import { useTimelineInteractionState, } from "@foxglove/studio-base/context/TimelineInteractionStateContext";
import { useAppTimeFormat } from "@foxglove/studio-base/hooks";
const useStyles = makeStyles()((theme) => ({
    tooltipDivider: {
        gridColumn: "span 2",
        marginBlock: theme.spacing(0.5),
        opacity: 0.5,
    },
    tooltipWrapper: {
        fontFeatureSettings: `${theme.typography.fontFeatureSettings}, "zero"`,
        fontFamily: theme.typography.body1.fontFamily,
        whiteSpace: "nowrap",
        columnGap: theme.spacing(0.5),
        display: "grid",
        alignItems: "center",
        gridTemplateColumns: "auto auto",
        width: "100%",
        flexDirection: "column",
    },
    itemKey: {
        fontSize: "0.7rem",
        opacity: 0.7,
        textAlign: "end",
        textTransform: "lowercase",
    },
}));
const selectHoveredEvents = (store) => store.eventsAtHoverValue;
const selectStartTime = (ctx) => ctx.playerState.activeData?.startTime;
export function PlaybackControlsTooltipContent(params) {
    const { stamp } = params;
    const { timeFormat, formatTime, formatDate } = useAppTimeFormat();
    const hoveredEvents = useTimelineInteractionState(selectHoveredEvents);
    const startTime = useMessagePipeline(selectStartTime);
    const { classes } = useStyles();
    if (!startTime) {
        return ReactNull;
    }
    const timeFromStart = subtractTimes(stamp, startTime);
    const tooltipItems = [];
    if (!_.isEmpty(hoveredEvents)) {
        Object.values(hoveredEvents).forEach(({ event }) => {
            tooltipItems.push({
                type: "item",
                title: "开始",
                value: formatTime(event.startTime),
            });
            tooltipItems.push({
                type: "item",
                title: "结束",
                value: formatTime(event.endTime),
            });
            if (!_.isEmpty(event.metadata)) {
                Object.entries(event.metadata).forEach(([metaKey, metaValue]) => {
                    tooltipItems.push({ type: "item", title: metaKey, value: metaValue });
                });
            }
            tooltipItems.push({ type: "divider" });
        });
    }
    switch (timeFormat) {
        case "TOD":
            tooltipItems.push({ type: "item", title: "日期", value: formatDate(stamp) });
            tooltipItems.push({ type: "item", title: "时间", value: formatTime(stamp) });
            break;
        case "SEC":
            tooltipItems.push({ type: "item", title: "SEC", value: formatTime(stamp) });
            break;
    }
    tooltipItems.push({
        type: "item",
        title: "已用时间",
        value: `${toSec(timeFromStart).toFixed(9)} sec`,
    });
    return (_jsx("div", { className: classes.tooltipWrapper, children: tooltipItems.map((item, idx) => {
            if (item.type === "divider") {
                return _jsx(Divider, { className: classes.tooltipDivider }, `divider_${idx}`);
            }
            return (_jsxs(Fragment, { children: [_jsx(Typography, { className: classes.itemKey, noWrap: true, children: item.title }), _jsx(Typography, { variant: "subtitle2", noWrap: true, children: item.value })] }, `${item.title}_${idx}`));
        }) }));
}
