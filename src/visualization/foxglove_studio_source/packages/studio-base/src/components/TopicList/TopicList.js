import { jsx as _jsx, Fragment as _Fragment, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import ClearIcon from "@mui/icons-material/Clear";
import SearchIcon from "@mui/icons-material/Search";
import { IconButton, List, ListItem, ListItemText, Skeleton, TextField, } from "@mui/material";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { useLatest } from "react-use";
import { AutoSizer } from "react-virtualized";
import { VariableSizeList } from "react-window";
import { makeStyles } from "tss-react/mui";
import { useDebounce } from "use-debounce";
import { filterMap } from "@foxglove/den/collection";
import { quoteTopicNameIfNeeded } from "@foxglove/message-path";
import { useDataSourceInfo } from "@foxglove/studio-base/PanelAPI";
import { DirectTopicStatsUpdater } from "@foxglove/studio-base/components/DirectTopicStatsUpdater";
import EmptyState from "@foxglove/studio-base/components/EmptyState";
import { useMessagePipeline, } from "@foxglove/studio-base/components/MessagePipeline";
import { ContextMenu } from "@foxglove/studio-base/components/TopicList/ContextMenu";
import { PlayerPresence } from "@foxglove/studio-base/players/types";
import { MessagePathSelectionProvider } from "@foxglove/studio-base/services/messagePathDragging/MessagePathSelectionProvider";
import { MessagePathRow } from "./MessagePathRow";
import { TopicRow } from "./TopicRow";
import { useMultiSelection } from "./useMultiSelection";
import { useTopicListSearch } from "./useTopicListSearch";
const selectPlayerPresence = ({ playerState }) => playerState.presence;
const useStyles = makeStyles()((theme) => ({
    root: {
        width: "100%",
        height: "100%",
        overflow: "hidden",
        display: "flex",
        flexDirection: "column",
        containerType: "inline-size",
    },
    filterBar: {
        top: 0,
        zIndex: theme.zIndex.appBar,
        padding: theme.spacing(0.5),
        position: "sticky",
        backgroundColor: theme.palette.background.paper,
    },
    filterStartAdornment: {
        display: "flex",
    },
    skeletonText: {
        marginTop: theme.spacing(0.5),
        marginBottom: theme.spacing(0.5),
    },
}));
function getDraggedMessagePath(treeItem) {
    switch (treeItem.type) {
        case "topic":
            return {
                path: quoteTopicNameIfNeeded(treeItem.item.item.name),
                rootSchemaName: treeItem.item.item.schemaName,
                isTopic: true,
                isLeaf: false,
                topicName: treeItem.item.item.name,
            };
        case "schema":
            return {
                path: treeItem.item.item.fullPath,
                rootSchemaName: treeItem.item.item.topic.schemaName,
                isTopic: false,
                isLeaf: treeItem.item.item.suffix.isLeaf,
                topicName: treeItem.item.item.topic.name,
            };
    }
}
export function TopicList() {
    const { t } = useTranslation("topicList");
    const { classes } = useStyles();
    const [undebouncedFilterText, setFilterText] = useState("");
    const [debouncedFilterText] = useDebounce(undebouncedFilterText, 50);
    const playerPresence = useMessagePipeline(selectPlayerPresence);
    const { topics, datatypes } = useDataSourceInfo();
    const listRef = useRef(ReactNull);
    const treeItems = useTopicListSearch({
        topics,
        datatypes,
        filterText: debouncedFilterText,
    });
    const { selectedIndexes, onSelect, getSelectedIndexes } = useMultiSelection(treeItems);
    const [contextMenuState, setContextMenuState] = useState(undefined);
    const latestTreeItems = useLatest(treeItems);
    const getSelectedItemsAsDraggedMessagePaths = useCallback(() => {
        return filterMap(Array.from(getSelectedIndexes()).sort(), (index) => latestTreeItems.current[index]
            ? getDraggedMessagePath(latestTreeItems.current[index])
            : undefined);
    }, [getSelectedIndexes, latestTreeItems]);
    const handleContextMenu = useCallback((event, index) => {
        event.preventDefault();
        const latestSelectedIndexes = getSelectedIndexes();
        // Select only the clicked item if it was not already selected
        if (!latestSelectedIndexes.has(index)) {
            onSelect({ index, modKey: false, shiftKey: false });
        }
        setContextMenuState({
            position: { left: event.clientX, top: event.clientY },
            items: getSelectedItemsAsDraggedMessagePaths(),
        });
    }, [getSelectedIndexes, getSelectedItemsAsDraggedMessagePaths, onSelect]);
    const handleContextMenuClose = useCallback(() => {
        setContextMenuState(undefined);
    }, []);
    useEffect(() => {
        // Discard cached row heights when the filter results change
        listRef.current?.resetAfterIndex(0);
    }, [treeItems]);
    const itemData = useMemo(() => ({ treeItems, selectedIndexes }), [selectedIndexes, treeItems]);
    const renderRow = useCallback(
    // `data` comes from the `itemData` we pass to the VariableSizeList below
    ({ index, style, data }) => {
        const treeItem = data.treeItems[index];
        const selected = data.selectedIndexes.has(index);
        const onClick = (event) => {
            event.preventDefault();
            onSelect({
                index,
                modKey: event.metaKey || event.ctrlKey,
                shiftKey: event.shiftKey,
            });
        };
        switch (treeItem.type) {
            case "topic":
                return (_jsx(TopicRow, { style: style, topicResult: treeItem.item, selected: selected, onClick: onClick, onContextMenu: (event) => {
                        handleContextMenu(event, index);
                    } }));
            case "schema":
                return (_jsx(MessagePathRow, { style: style, messagePathResult: treeItem.item, selected: selected, onClick: onClick, onContextMenu: (event) => {
                        handleContextMenu(event, index);
                    } }));
        }
    }, [handleContextMenu, onSelect]);
    if (playerPresence === PlayerPresence.NOT_PRESENT) {
        return _jsx(EmptyState, { children: t("noDataSourceSelected") });
    }
    if (playerPresence === PlayerPresence.ERROR) {
        return _jsx(EmptyState, { children: t("anErrorOccurred") });
    }
    if (playerPresence === PlayerPresence.INITIALIZING) {
        return (_jsxs(_Fragment, { children: [_jsx("header", { className: classes.filterBar, children: _jsx(TextField, { disabled: true, variant: "filled", fullWidth: true, placeholder: t("waitingForData"), InputProps: {
                            size: "small",
                            startAdornment: _jsx(SearchIcon, { fontSize: "small" }),
                        } }) }), _jsx(List, { dense: true, disablePadding: true, children: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15].map((i) => (_jsx(ListItem, { divider: true, children: _jsx(ListItemText, { className: classes.skeletonText, primary: _jsx(Skeleton, { animation: false, width: "20%" }), secondary: _jsx(Skeleton, { animation: "wave", width: "55%" }), secondaryTypographyProps: { variant: "caption" } }) }, i))) })] }));
    }
    return (_jsxs(MessagePathSelectionProvider, { getSelectedItems: getSelectedItemsAsDraggedMessagePaths, children: [_jsxs("div", { className: classes.root, children: [_jsx("header", { className: classes.filterBar, children: _jsx(TextField, { id: "topic-filter", variant: "filled", disabled: playerPresence !== PlayerPresence.PRESENT, onChange: (event) => {
                                setFilterText(event.target.value);
                            }, value: undebouncedFilterText, fullWidth: true, placeholder: t("searchBarPlaceholder"), InputProps: {
                                inputProps: { "data-testid": "topic-filter" },
                                size: "small",
                                startAdornment: (_jsx("label", { className: classes.filterStartAdornment, htmlFor: "topic-filter", children: _jsx(SearchIcon, { fontSize: "small" }) })),
                                endAdornment: undebouncedFilterText && (_jsx(IconButton, { size: "small", title: t("clearFilter"), onClick: () => {
                                        setFilterText("");
                                    }, edge: "end", children: _jsx(ClearIcon, { fontSize: "small" }) })),
                            } }) }), treeItems.length > 0 ? (_jsx("div", { style: { flex: "1 1 100%" }, children: _jsx(AutoSizer, { children: ({ width, height }) => (_jsx(VariableSizeList, { ref: listRef, width: width, height: height, itemCount: treeItems.length, itemSize: (index) => (treeItems[index]?.type === "topic" ? 50 : 28), itemData: itemData, overscanCount: 10, children: renderRow })) }) })) : (_jsxs(EmptyState, { children: [playerPresence === PlayerPresence.PRESENT && undebouncedFilterText
                                ? `${t("noTopicsOrDatatypesMatching")} \n “${undebouncedFilterText}”`
                                : t("noTopicsAvailable"), playerPresence === PlayerPresence.RECONNECTING && t("waitingForConnection")] })), _jsx(DirectTopicStatsUpdater, { interval: 6 })] }), contextMenuState && (_jsx(ContextMenu, { onClose: handleContextMenuClose, anchorPosition: contextMenuState.position, messagePaths: contextMenuState.items }))] }));
}
