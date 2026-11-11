import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { ReOrderDotsVertical16Filled } from "@fluentui/react-icons";
import { Fade, ListItem, ListItemButton, ListItemText, Tooltip, Typography } from "@mui/material";
import { useCallback, useEffect, useRef } from "react";
import { useDrag } from "react-dnd";
import { MosaicDragType } from "react-mosaic-component";
import { makeStyles } from "tss-react/mui";
import Stack from "@foxglove/studio-base/components/Stack";
import TextHighlight from "@foxglove/studio-base/components/TextHighlight";
const useStyles = makeStyles()((theme, _params, classes) => {
    return {
        listItemButton: {
            height: theme.spacing(4), // hard coded here because the parent element of this changes based on context
            cursor: "grab",
            [`&:not(:hover) .${classes.dragIcon}`]: {
                visibility: "hidden",
            },
        },
        dragIcon: {
            cursor: "grab",
            marginRight: theme.spacing(-1),
            color: theme.palette.text.disabled,
        },
    };
});
export function PanelListItem(props) {
    const { searchQuery, panel, onClick, onDragStart, onDrop, checked = false, highlighted = false, mosaicId, } = props;
    const { classes } = useStyles();
    const scrollRef = useRef(ReactNull);
    const [, connectDragSource] = useDrag({
        type: MosaicDragType.WINDOW,
        // mosaicId is needed for react-mosaic to accept the drop
        item: () => {
            onDragStart?.();
            return { mosaicId };
        },
        options: { dropEffect: "copy" },
        end: (_item, monitor) => {
            const dropResult = monitor.getDropResult();
            // do nothing when the user wants to cancel a dragged panel
            if (dropResult == undefined || !monitor.didDrop()) {
                return;
            }
            const { position, path, tabId } = dropResult;
            // dropping outside mosaic does nothing. If we have a tabId, but no
            // position or path, we're dragging into an empty tab.
            if ((position == undefined || path == undefined) && tabId == undefined) {
                // when dragging a panel into an empty layout treat it link clicking the panel
                // mosaic doesn't give us a position or path to invoke onDrop
                onClick();
                return;
            }
            const { type, config } = panel;
            onDrop({ type, config, position, path, tabId });
        },
    });
    useEffect(() => {
        if (highlighted && scrollRef.current) {
            const highlightedItem = scrollRef.current.getBoundingClientRect();
            const scrollContainer = scrollRef.current.parentElement?.parentElement?.parentElement;
            if (scrollContainer) {
                const scrollContainerToTop = scrollContainer.getBoundingClientRect().top;
                const isInView = highlightedItem.top >= 0 &&
                    highlightedItem.top >= scrollContainerToTop &&
                    highlightedItem.top + 50 <= window.innerHeight;
                if (!isInView) {
                    scrollRef.current.scrollIntoView();
                }
            }
        }
    }, [highlighted]);
    const mergedRef = useCallback((el) => {
        connectDragSource(el);
        scrollRef.current = el;
    }, [connectDragSource, scrollRef]);
    const targetString = panel.extensionNamespace
        ? `${panel.title} [${panel.extensionNamespace}]`
        : panel.title;
    const onClickWithStopPropagation = useCallback((event) => {
        event.stopPropagation();
        onClick();
    }, [onClick]);
    return (_jsx(Tooltip, { placement: "right", enterDelay: 500, leaveDelay: 0, TransitionComponent: Fade, title: _jsxs(Stack, { paddingTop: 0.25, style: { width: 200 }, children: [panel.thumbnail != undefined && _jsx("img", { src: panel.thumbnail, alt: panel.title }), _jsxs(Stack, { padding: 1, gap: 0.5, children: [_jsx(Typography, { variant: "body2", fontWeight: "bold", children: panel.title }), _jsx(Typography, { variant: "body2", style: { opacity: 0.6 }, children: panel.description })] })] }), children: _jsx(ListItem, { dense: true, disablePadding: true, children: _jsxs(ListItemButton, { selected: highlighted, className: classes.listItemButton, disabled: checked, ref: mergedRef, onClick: onClickWithStopPropagation, children: [_jsx(ListItemText, { children: _jsx("span", { "data-testid": `panel-menu-item ${panel.title}`, children: _jsx(TextHighlight, { targetStr: targetString, searchText: searchQuery }) }) }), _jsx(ReOrderDotsVertical16Filled, { className: classes.dragIcon })] }) }) }));
}
