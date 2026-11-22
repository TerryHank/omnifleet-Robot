import { jsx as _jsx, Fragment as _Fragment, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { Typography } from "@mui/material";
import { useMemo } from "react";
import { makeStyles } from "tss-react/mui";
import Stack from "@foxglove/studio-base/components/Stack";
import { useAppTimeFormat } from "@foxglove/studio-base/hooks";
import { isAbsoluteTime, formatTimeRaw } from "@foxglove/studio-base/util/time";
const useStyles = makeStyles()((theme) => ({
    numericValue: {
        fontFeatureSettings: `${theme.typography.fontFeatureSettings}, "zero"`,
    },
}));
export default function Timestamp(props) {
    const { classes } = useStyles();
    const { disableDate = false, horizontal = false, time, title } = props;
    const { formatDate, formatTime } = useAppTimeFormat();
    const currentTimeStr = useMemo(() => formatTime(time), [time, formatTime]);
    const rawTimeStr = useMemo(() => formatTimeRaw(time), [time]);
    const date = useMemo(() => formatDate(time), [formatDate, time]);
    if (!isAbsoluteTime(time)) {
        return (_jsx(Stack, { title: title, direction: "row", alignItems: "center", flexGrow: 0, children: _jsx(Typography, { className: classes.numericValue, variant: "inherit", children: rawTimeStr }) }));
    }
    return (_jsxs(Stack, { title: title, gap: horizontal ? 0 : 1, flexWrap: horizontal ? "nowrap" : "wrap", direction: horizontal ? "row" : "column", alignItems: horizontal ? "center" : "flex-start", justifyContent: horizontal ? "flex-start" : "center", children: [!disableDate && (_jsxs(_Fragment, { children: [_jsx(Typography, { className: classes.numericValue, noWrap: true, fontWeight: !horizontal ? 700 : undefined, variant: "inherit", children: date }), horizontal && _jsx(_Fragment, { children: "\u00A0" })] })), _jsx(Stack, { direction: "row", alignItems: "center", flexShrink: 0, gap: 0.5, children: _jsx(Typography, { variant: "inherit", className: classes.numericValue, children: currentTimeStr }) })] }));
}
