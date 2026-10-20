import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { Divider, Typography } from "@mui/material";
import { makeStyles } from "tss-react/mui";
import CopyButton from "@foxglove/studio-base/components/CopyButton";
import { DirectTopicStatsUpdater } from "@foxglove/studio-base/components/DirectTopicStatsUpdater";
import EmptyState from "@foxglove/studio-base/components/EmptyState";
import { useMessagePipeline, } from "@foxglove/studio-base/components/MessagePipeline";
import Panel from "@foxglove/studio-base/components/Panel";
import PanelToolbar from "@foxglove/studio-base/components/PanelToolbar";
import Stack from "@foxglove/studio-base/components/Stack";
const useStyles = makeStyles()((theme, _params, classes) => ({
    copyIcon: {
        visibility: "hidden",
        "&:hover": {
            backgroundColor: "transparent",
        },
    },
    table: {
        borderCollapse: "collapse",
        display: "block",
        flex: 1,
        thead: {
            position: "sticky",
            textAlign: "left",
            top: 0,
            zIndex: theme.zIndex.appBar - 1,
        },
        tr: {
            "&:hover": {
                backgroundColor: theme.palette.background.paper,
            },
        },
        th: {
            backgroundColor: theme.palette.background.paper,
            paddingBlock: theme.spacing(1),
            paddingInline: theme.spacing(1.5),
            whiteSpace: "nowrap",
            width: "100%",
        },
        td: {
            paddingBlock: theme.spacing(0.25),
            paddingInline: theme.spacing(1.5),
            whiteSpace: "nowrap",
            [`&:hover .${classes.copyIcon}`]: {
                visibility: "visible",
            },
        },
    },
}));
function TopicRow({ topic }) {
    const { classes } = useStyles();
    return (_jsxs("tr", { children: [_jsxs("td", { children: [topic.name, _jsx(CopyButton, { className: classes.copyIcon, edge: "end", size: "small", iconSize: "small", getText: () => topic.name }), topic.aliasedFromName && (_jsxs(Typography, { variant: "subtitle2", fontSize: "0.5rem", children: ["from ", topic.aliasedFromName] }))] }), _jsx("td", { children: topic.schemaName == undefined ? ("—") : (_jsxs(_Fragment, { children: [topic.schemaName, _jsx(CopyButton, { className: classes.copyIcon, edge: "end", size: "small", iconSize: "small", getText: () => topic.schemaName ?? "" })] })) }), _jsx("td", { "data-topic": topic.name, "data-topic-stat": "count", children: "\u2014" }), _jsx("td", { "data-topic": topic.name, "data-topic-stat": "frequency", children: "\u2014" })] }));
}
const selectSortedTopics = (ctx) => ctx.sortedTopics;
const selectStartTime = (ctx) => ctx.playerState.activeData?.startTime;
const selectEndTime = (ctx) => ctx.playerState.activeData?.endTime;
const MemoTopicRow = React.memo(TopicRow);
function SourceInfo() {
    const { classes } = useStyles();
    const topics = useMessagePipeline(selectSortedTopics);
    const startTime = useMessagePipeline(selectStartTime);
    const endTime = useMessagePipeline(selectEndTime);
    if (!startTime || !endTime) {
        return (_jsxs(_Fragment, { children: [_jsx(PanelToolbar, {}), _jsx(EmptyState, { children: "\u6B63\u5728\u7B49\u5F85\u6570\u636E\u2026\u2026" })] }));
    }
    return (_jsxs(_Fragment, { children: [_jsx(PanelToolbar, {}), _jsx(Divider, {}), _jsxs(Stack, { fullHeight: true, overflowY: "auto", children: [_jsxs("table", { className: classes.table, children: [_jsx("thead", { children: _jsxs("tr", { children: [_jsx("th", { children: "Topic Name" }), _jsx("th", { children: "Datatype" }), _jsx("th", { children: "Message count" }), _jsx("th", { children: "Frequency" })] }) }), _jsx("tbody", { children: topics.map((topic) => (_jsx(MemoTopicRow, { topic: topic }, topic.name))) })] }), _jsx(DirectTopicStatsUpdater, { interval: 6 })] })] }));
}
SourceInfo.panelType = "SourceInfo";
SourceInfo.defaultConfig = {};
export default Panel(SourceInfo);
