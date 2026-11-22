import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
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
import { useCallback } from "react";
import { makeStyles } from "tss-react/mui";
const DEFAULT_END_TEXT_LENGTH = 16;
const useStyles = makeStyles()(() => ({
    root: {
        display: "flex",
        justifyContent: "flex-start",
        overflow: "hidden",
        userSelect: "all",
    },
    start: {
        overflow: "hidden",
        textOverflow: "ellipsis",
        whiteSpace: "nowrap",
        flexShrink: 1,
    },
    end: {
        whiteSpace: "nowrap",
        flexBasis: "content",
        flexGrow: 0,
        flexShrink: 0,
        maxWidth: "100%",
        overflow: "hidden",
        textOverflow: "ellipsis",
    },
}));
export default function TextMiddleTruncate({ text, endTextLength, className, style, }) {
    const { classes, cx } = useStyles();
    let startTextLen = Math.max(0, text.length -
        (endTextLength == undefined || endTextLength === 0 ? DEFAULT_END_TEXT_LENGTH : endTextLength));
    // Don't split at or immediately after whitespace.
    while (startTextLen < text.length && text.charAt(startTextLen).match(/\s/)) {
        startTextLen += 2;
    }
    const startText = text.substring(0, startTextLen);
    const endText = text.substring(startTextLen);
    // Copy the full text to the clipboard manually. Otherwise the browser will insert a
    // newline into the copied text since it spans two DOM nodes.
    const onCopy = useCallback((event) => {
        event.preventDefault();
        event.stopPropagation();
        const clipboardData = event.clipboardData;
        clipboardData.setData("text/plain", text);
    }, [text]);
    if (!startText) {
        return (_jsx("div", { className: cx(classes.end, className), style: style, children: endText }));
    }
    return (_jsxs("div", { "data-testid": "text-middle-truncate", className: cx(className, classes.root), title: text, style: style, onCopy: onCopy, children: [_jsx("div", { className: classes.start, children: startText }), _jsx("div", { className: classes.end, children: endText })] }));
}
