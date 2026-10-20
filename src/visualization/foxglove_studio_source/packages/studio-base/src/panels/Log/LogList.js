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
import DoubleArrowDownIcon from "@mui/icons-material/KeyboardDoubleArrowDown";
import { Fab } from "@mui/material";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useResizeDetector } from "react-resize-detector";
import { useLatest } from "react-use";
import { AutoSizer } from "react-virtualized";
import { VariableSizeList as List } from "react-window";
import { makeStyles } from "tss-react/mui";
import { useAppTimeFormat } from "@foxglove/studio-base/hooks";
import LogMessage from "./LogMessage";
const useStyles = makeStyles()((theme) => ({
    floatingButton: {
        position: "absolute",
        bottom: 0,
        right: 0,
        margin: theme.spacing(1.5),
    },
}));
function Row(props) {
    const { timeFormat, timeZone } = useAppTimeFormat();
    const ref = useRef(ReactNull);
    useEffect(() => {
        if (ref.current) {
            props.data.setRowHeight(props.index, ref.current.clientHeight);
        }
    }, [props.data, props.index]);
    const item = props.data.items[props.index];
    return (_jsx("div", { style: { ...props.style, height: "auto" }, ref: ref, children: _jsx(LogMessage, { value: item, timestampFormat: timeFormat, timeZone: timeZone }) }));
}
/**
 * List for showing large number of items, which are expected to be appended to the end regularly.
 * Automatically scrolls to the bottom unless you explicitly scroll up.
 */
function LogList({ items }) {
    const { classes } = useStyles();
    // Reference to the list item itself.
    const listRef = useRef(ReactNull);
    // Reference to the outer list div. Needed for autoscroll determination.
    const outerRef = useRef(ReactNull);
    const latestItems = useLatest(items);
    // Automatically scroll to reveal new items.
    const [autoscrollToEnd, setAutoscrollToEnd] = useState(true);
    const onResetView = React.useCallback(() => {
        setAutoscrollToEnd(true);
        listRef.current?.scrollToItem(latestItems.current.length - 1, "end");
    }, [latestItems]);
    useEffect(() => {
        if (autoscrollToEnd) {
            listRef.current?.scrollToItem(items.length - 1, "end");
        }
    }, [autoscrollToEnd, items.length]);
    // Disable autoscroll if the user manually scrolls back.
    const onScroll = React.useCallback(({ scrollDirection, scrollOffset, scrollUpdateWasRequested, }) => {
        const isAtEnd = scrollOffset + (outerRef.current?.offsetHeight ?? 0) === outerRef.current?.scrollHeight;
        if (!scrollUpdateWasRequested && scrollDirection === "backward" && !isAtEnd) {
            setAutoscrollToEnd(false);
        }
        else if (scrollDirection === "forward" && isAtEnd) {
            setAutoscrollToEnd(true);
        }
    }, []);
    // Cache calculated item heights.
    const itemHeightCache = useRef({});
    const getRowHeight = useCallback((index) => itemHeightCache.current[index] ?? 16, []);
    const setRowHeight = useCallback((index, height) => {
        itemHeightCache.current[index] = height;
        listRef.current?.resetAfterIndex(index);
    }, []);
    const { width: resizedWidth, ref: resizeRootRef } = useResizeDetector({
        refreshRate: 0,
        refreshMode: "debounce",
    });
    // This is passed to each row to tell it what to render.
    const itemData = useMemo(() => ({
        items,
        setRowHeight,
    }), 
    // Add resized width as an extra dep here to force the list to recalculate
    // everything when the width changes.
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [items, setRowHeight, resizedWidth]);
    return (_jsx(AutoSizer, { children: ({ width, height }) => {
            return (_jsxs("div", { style: { position: "relative", width, height }, ref: resizeRootRef, children: [_jsx(List, { ref: listRef, width: width, height: height, style: { outline: "none" }, itemData: itemData, itemSize: getRowHeight, itemCount: items.length, outerRef: outerRef, onScroll: onScroll, children: Row }), !autoscrollToEnd && (_jsx(Fab, { size: "small", title: "\u6EDA\u52A8\u5230\u5E95\u90E8", onClick: onResetView, className: classes.floatingButton, children: _jsx(DoubleArrowDownIcon, {}) }))] }));
        } }));
}
export default LogList;
