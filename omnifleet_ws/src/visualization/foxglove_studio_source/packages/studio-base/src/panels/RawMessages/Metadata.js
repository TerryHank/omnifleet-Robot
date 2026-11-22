import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
//
// This file incorporates work covered by the following copyright and
// permission notice:
//
//   Copyright 2019-2021 Cruise LLC
//
//   This source code is licensed under the Apache License, Version 2.0,
//   found at http://www.apache.org/licenses/LICENSE-2.0
//   You may not use this file except in compliance with the License.
import { Link, Typography } from "@mui/material";
import { useCallback } from "react";
import { useLatest } from "react-use";
import { makeStyles } from "tss-react/mui";
import CopyButton from "@foxglove/studio-base/components/CopyButton";
import Stack from "@foxglove/studio-base/components/Stack";
import { formatTimeRaw } from "@foxglove/studio-base/util/time";
import { copyMessageReplacer } from "./copyMessageReplacer";
import { getMessageDocumentationLink } from "./utils";
const useStyles = makeStyles()((theme) => ({
    button: {
        padding: theme.spacing(0.125),
        ".MuiSvgIcon-root": {
            fontSize: `${theme.typography.pxToRem(16)} !important`,
        },
        ".MuiButton-startIcon": {
            marginRight: theme.spacing(0.5),
        },
        "&:hover": {
            backgroundColor: "transparent",
        },
    },
}));
export default function Metadata({ data, diffData, diff, datatype, message, diffMessage, }) {
    const { classes } = useStyles();
    // Access these by ref so that our callbacks aren't invalidated and CopyButton
    // memoization is stable.
    const latestData = useLatest(data);
    const latestDiffData = useLatest(diffData);
    const docsLink = datatype ? getMessageDocumentationLink(datatype) : undefined;
    const copyData = useCallback(() => JSON.stringify(latestData.current, copyMessageReplacer, 2) ?? "", [latestData]);
    const copyDiffData = useCallback(() => JSON.stringify(latestDiffData.current, copyMessageReplacer, 2) ?? "", [latestDiffData]);
    const copyDiff = useCallback(() => JSON.stringify(diff, copyMessageReplacer, 2) ?? "", [diff]);
    return (_jsxs(Stack, { alignItems: "flex-start", paddingInline: 0.25, paddingBlockStart: 0.75, children: [_jsxs(Stack, { direction: "row", alignItems: "center", gap: 0.5, children: [_jsxs(Typography, { variant: "caption", lineHeight: 1.2, color: "text.secondary", children: [diffMessage ? ("base") : docsLink ? (_jsx(Link, { target: "_blank", color: "inherit", variant: "caption", underline: "hover", rel: "noopener noreferrer", href: docsLink, children: datatype })) : (datatype), ` @ ${formatTimeRaw(message.receiveTime)} sec`] }), _jsx(CopyButton, { size: "small", iconSize: "small", className: classes.button, getText: copyData })] }), diffMessage?.receiveTime && (_jsxs(_Fragment, { children: [_jsxs(Stack, { direction: "row", alignItems: "center", gap: 0.5, children: [_jsx(Typography, { variant: "caption", lineHeight: 1.2, color: "text.secondary", children: `diff @ ${formatTimeRaw(diffMessage.receiveTime)} sec ` }), _jsx(CopyButton, { size: "small", iconSize: "small", className: classes.button, getText: copyDiffData })] }), _jsx(CopyButton, { size: "small", iconSize: "small", className: classes.button, getText: copyDiff, children: "Copy diff of msgs" })] }))] }));
}
