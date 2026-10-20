import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { ReOrderDotsVertical16Regular } from "@fluentui/react-icons";
import { Badge, Typography } from "@mui/material";
import { useCallback, useMemo } from "react";
import { quoteTopicNameIfNeeded } from "@foxglove/message-path";
import { HighlightChars } from "@foxglove/studio-base/components/HighlightChars";
import Stack from "@foxglove/studio-base/components/Stack";
import { useMessagePathDrag } from "@foxglove/studio-base/services/messagePathDragging";
import { TopicStatsChip } from "./TopicStatsChip";
import { useTopicListStyles } from "./useTopicListStyles";
export function TopicRow({ topicResult, style, selected, onClick, onContextMenu, }) {
    const { cx, classes } = useTopicListStyles();
    const topic = topicResult.item;
    const item = useMemo(() => ({
        path: quoteTopicNameIfNeeded(topic.name),
        rootSchemaName: topic.schemaName,
        isTopic: true,
        isLeaf: false,
        topicName: topic.name,
    }), [topic.name, topic.schemaName]);
    const { connectDragSource, connectDragPreview, cursor, isDragging, draggedItemCount } = useMessagePathDrag({
        item,
        selected,
    });
    const combinedRef = useCallback((el) => {
        connectDragSource(el);
        connectDragPreview(el);
    }, [connectDragPreview, connectDragSource]);
    return (_jsxs("div", { ref: combinedRef, className: cx(classes.row, {
            [classes.isDragging]: isDragging,
            [classes.selected]: selected,
        }), style: { ...style, cursor }, onClick: onClick, onContextMenu: onContextMenu, children: [draggedItemCount > 1 && (_jsx(Badge, { color: "primary", className: classes.countBadge, badgeContent: draggedItemCount })), _jsxs(Stack, { flex: "auto", alignItems: "flex-start", overflow: "hidden", children: [_jsxs(Typography, { variant: "body2", noWrap: true, className: classes.textContent, children: [_jsx(HighlightChars, { str: topic.name, indices: topicResult.positions }), topic.aliasedFromName != undefined && (_jsxs(Typography, { variant: "caption", className: classes.aliasedTopicName, children: ["from ", topic.aliasedFromName] }))] }), topic.schemaName != undefined && (_jsx(Typography, { variant: "caption", color: "text.secondary", noWrap: true, className: classes.textContent, children: _jsx(HighlightChars, { str: topic.schemaName, indices: topicResult.positions, offset: topic.name.length + 1 }) }))] }), _jsx(TopicStatsChip, { selected: selected, topicName: topic.name }), _jsx("div", { "data-testid": "TopicListDragHandle", className: classes.dragHandle, children: _jsx(ReOrderDotsVertical16Regular, {}) })] }));
}
