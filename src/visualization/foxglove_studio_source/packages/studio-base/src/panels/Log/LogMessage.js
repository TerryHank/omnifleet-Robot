import { jsxs as _jsxs, jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
//
// This file incorporates work covered by the following copyright and
// permission notice:
//
//   Copyright 2018-2021 Cruise LLC
//
//   This source code is licensed under the Apache License, Version 2.0,
//   found at http://www.apache.org/licenses/LICENSE-2.0
//   You may not use this file except in compliance with the License.
import * as _ from "lodash-es";
import { makeStyles } from "tss-react/mui";
import useLogStyles from "@foxglove/studio-base/panels/Log/useLogStyles";
import LevelToString from "./LevelToString";
import Stamp from "./Stamp";
const useStyles = makeStyles()((theme) => ({
    root: {
        // Subsequent lines are indented bu using left padding, so we undo the padding for the first line
        // with textIndent
        textIndent: -20,
        paddingLeft: 20,
        whiteSpace: "pre-wrap",
        paddingTop: 1,
        paddingBottom: 1,
        lineHeight: 1,
        fontFamily: theme.typography.fontMonospace,
        wordBreak: "break-word",
    },
}));
export default React.memo(function LogMessage(props) {
    const { value: msg, timestampFormat, timeZone } = props;
    const { classes, cx } = useStyles();
    const { classes: logClasses } = useLogStyles();
    const altStr = `${msg.file}:${msg.line}`;
    const strLevel = LevelToString(msg.level);
    const stamp = msg.stamp;
    // the first message line is rendered with the info/stamp/name
    // following newlines are rendered on their own line
    const lines = msg.message.split("\n");
    return (_jsxs("div", { title: altStr, className: cx(classes.root, {
            [logClasses.fatal]: strLevel === "FATAL",
            [logClasses.error]: strLevel === "ERROR",
            [logClasses.warn]: strLevel === "WARN",
            [logClasses.info]: strLevel === "INFO",
            [logClasses.debug]: strLevel === "DEBUG",
        }), children: [_jsxs("div", { children: [_jsxs("span", { children: ["[", _.padStart(strLevel, 5, " "), "]"] }), _jsxs("span", { children: ["[", _jsx(Stamp, { stamp: stamp, timestampFormat: timestampFormat, timeZone: timeZone }), "]"] }), msg.name != undefined && _jsxs("span", { children: ["[", msg.name, "]:"] }), _jsx("span", { children: "\u00A0" }), _jsx("span", { children: lines[0] })] }), _jsx("div", { children: lines.slice(1).map((line, idx) => {
                    return (_jsxs("div", { children: ["\u00A0\u00A0\u00A0\u00A0", line] }, idx));
                }) })] }));
});
