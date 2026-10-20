import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { ReOrderDotsVertical16Regular } from "@fluentui/react-icons";
import { Badge, Typography } from "@mui/material";
import { useCallback, useMemo } from "react";
import { HighlightChars } from "@foxglove/studio-base/components/HighlightChars";
import Stack from "@foxglove/studio-base/components/Stack";
import { useMessagePathDrag } from "@foxglove/studio-base/services/messagePathDragging";
import { useTopicListStyles } from "./useTopicListStyles";
export function MessagePathRow({ messagePathResult, style, selected, onClick, onContextMenu, }) {
    const { cx, classes } = useTopicListStyles();
    const { fullPath, suffix: { pathSuffix, type, isLeaf }, topic, } = messagePathResult.item;
    const item = useMemo(() => ({
        path: fullPath,
        rootSchemaName: topic.schemaName,
        isTopic: false,
        isLeaf,
        topicName: topic.name,
    }), [fullPath, isLeaf, topic.name, topic.schemaName]);
    const { connectDragSource, connectDragPreview, cursor, isDragging, draggedItemCount } = useMessagePathDrag({
        item,
        selected,
    });
    const combinedRef = useCallback((el) => {
        connectDragSource(el);
        connectDragPreview(el);
    }, [connectDragPreview, connectDragSource]);
    return (_jsxs("div", { ref: combinedRef, className: cx(classes.row, classes.fieldRow, {
            [classes.isDragging]: isDragging,
            [classes.selected]: selected,
        }), style: { ...style, cursor }, onClick: onClick, onContextMenu: onContextMenu, children: [draggedItemCount > 1 && (_jsx(Badge, { color: "primary", className: classes.countBadge, badgeContent: draggedItemCount })), _jsxs(Stack, { flex: "auto", direction: "row", gap: 2, overflow: "hidden", children: [_jsx(Typography, { variant: "body2", noWrap: true, children: _jsx(HighlightChars, { str: pathSuffix, indices: messagePathResult.positions, offset: messagePathResult.item.offset }) }), _jsx(Typography, { variant: "caption", color: "text.secondary", noWrap: true, children: type })] }), _jsx("div", { "data-testid": "TopicListDragHandle", style: { cursor }, className: classes.dragHandle, children: _jsx(ReOrderDotsVertical16Regular, {}) })] }));
}
