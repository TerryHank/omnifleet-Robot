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
import PushPinIcon from "@mui/icons-material/PushPin";
import { IconButton, InputBase, ListItem, ListItemButton, ListItemText, MenuItem, Select, Typography, iconButtonClasses, inputBaseClasses, listItemTextClasses, selectClasses, } from "@mui/material";
import { produce } from "immer";
import * as _ from "lodash-es";
import { useCallback, useEffect, useMemo } from "react";
import { AutoSizer } from "react-virtualized";
import { FixedSizeList as List } from "react-window";
import { makeStyles } from "tss-react/mui";
import { filterMap } from "@foxglove/den/collection";
import { useDataSourceInfo } from "@foxglove/studio-base/PanelAPI";
import EmptyState from "@foxglove/studio-base/components/EmptyState";
import Panel from "@foxglove/studio-base/components/Panel";
import { usePanelContext } from "@foxglove/studio-base/components/PanelContext";
import PanelToolbar from "@foxglove/studio-base/components/PanelToolbar";
import Stack from "@foxglove/studio-base/components/Stack";
import useDiagnostics from "@foxglove/studio-base/panels/diagnostics/useDiagnostics";
import useStaleTime from "@foxglove/studio-base/panels/diagnostics/useStaleTime";
import { usePanelSettingsTreeUpdate } from "@foxglove/studio-base/providers/PanelStateContextProvider";
import toggle from "@foxglove/studio-base/util/toggle";
import { buildSummarySettingsTree } from "./settings";
import { DEFAULT_SECONDS_UNTIL_STALE, KNOWN_LEVELS, LEVEL_NAMES, filterAndSortDiagnostics, getDiagnosticsByLevel, getDiagnosticsWithStales, } from "./util";
const MESSAGE_COLORS = {
    ok: "success.main",
    warn: "warning.main",
    error: "error.main",
    stale: "text.secondary",
};
const useStyles = makeStyles()((theme) => ({
    listItemButton: {
        padding: 0,
        [`.${iconButtonClasses.root}`]: {
            visibility: "hidden",
            "&:hover": {
                backgroundColor: "transparent",
            },
        },
        [`.${listItemTextClasses.root}`]: {
            gap: theme.spacing(1),
            display: "flex",
        },
        [`&:hover .${iconButtonClasses.root}`]: {
            visibility: "visible",
        },
    },
    select: {
        [`.${inputBaseClasses.input}.${selectClasses.select}.${inputBaseClasses.inputSizeSmall}`]: {
            paddingTop: 0,
            paddingBottom: 0,
            minWidth: 40,
        },
        [`.${listItemTextClasses.root}`]: {
            marginTop: 0,
            marginBottom: 0,
        },
    },
}));
const NodeRow = React.memo(function NodeRow(props) {
    const { info, isPinned, onClick, onClickPin } = props;
    const { classes } = useStyles();
    const handleClick = useCallback(() => {
        onClick(info);
    }, [onClick, info]);
    const handleClickPin = useCallback(() => {
        onClickPin(info);
    }, [onClickPin, info]);
    const levelName = LEVEL_NAMES[info.status.level];
    return (_jsx(ListItem, { dense: true, disablePadding: true, "data-testid-diagnostic-row": true, children: _jsxs(ListItemButton, { className: classes.listItemButton, disableGutters: true, onClick: handleClick, children: [_jsx(IconButton, { size: "small", onClick: (event) => {
                        handleClickPin();
                        event.stopPropagation();
                    }, style: isPinned ? { visibility: "visible" } : undefined, children: _jsx(PushPinIcon, { fontSize: "small", color: isPinned ? "inherit" : "disabled" }) }), _jsx(ListItemText, { primary: info.displayName, secondary: info.status.message, secondaryTypographyProps: {
                        color: MESSAGE_COLORS[levelName ?? "stale"],
                    }, style: { overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" } })] }) }));
});
const ALLOWED_DATATYPES = [
    "diagnostic_msgs/DiagnosticArray",
    "diagnostic_msgs/msg/DiagnosticArray",
    "ros.diagnostic_msgs.DiagnosticArray",
];
function DiagnosticSummary(props) {
    const { config, saveConfig } = props;
    const { classes } = useStyles();
    const { topics } = useDataSourceInfo();
    const { minLevel, topicToRender, pinnedIds, hardwareIdFilter, sortByLevel = true, secondsUntilStale = DEFAULT_SECONDS_UNTIL_STALE, } = config;
    const { openSiblingPanel } = usePanelContext();
    const updatePanelSettingsTree = usePanelSettingsTreeUpdate();
    const staleTime = useStaleTime(secondsUntilStale);
    const togglePinned = useCallback((info) => {
        saveConfig({ pinnedIds: toggle(pinnedIds, info.id) });
    }, [pinnedIds, saveConfig]);
    const showDetails = useCallback((info) => {
        openSiblingPanel({
            panelType: "DiagnosticStatusPanel",
            siblingConfigCreator: () => ({
                selectedHardwareId: info.status.hardware_id,
                selectedName: info.status.name,
                topicToRender,
                collapsedSections: [],
            }),
            updateIfExists: true,
        });
    }, [topicToRender, openSiblingPanel]);
    const renderRow = useCallback((renderProps) => {
        const item = renderProps.data[renderProps.index];
        return (_jsx("div", { style: { ...renderProps.style }, children: _jsx(NodeRow, { info: item, isPinned: pinnedIds.includes(item.id), onClick: showDetails, onClickPin: togglePinned }, item.id) }));
    }, [pinnedIds, showDetails, togglePinned]);
    // Filter down all topics to those that conform to our supported datatypes
    const availableTopics = useMemo(() => {
        const filtered = topics
            .filter((topic) => topic.schemaName != undefined && ALLOWED_DATATYPES.includes(topic.schemaName))
            .map((topic) => topic.name);
        // Keeps only the first occurrence of each topic.
        return _.uniq([...filtered]);
    }, [topics]);
    // If the topicToRender is not in the availableTopics, then we should not try to use it
    const diagnosticTopic = useMemo(() => {
        return availableTopics.includes(topicToRender) ? topicToRender : undefined;
    }, [availableTopics, topicToRender]);
    const diagnostics = useDiagnostics(diagnosticTopic);
    const diagnosticsWithOldMarkedAsStales = useMemo(() => {
        return staleTime ? getDiagnosticsWithStales(diagnostics, staleTime) : diagnostics;
    }, [diagnostics, staleTime]);
    const summary = useMemo(() => {
        if (diagnosticsWithOldMarkedAsStales.size === 0) {
            return (_jsxs(EmptyState, { children: ["Waiting for ", _jsx("code", { children: topicToRender }), " messages"] }));
        }
        const pinnedNodes = filterMap(pinnedIds, (id) => {
            const [, trimmedHardwareId, name] = id.split("|");
            if (name == undefined || trimmedHardwareId == undefined) {
                return;
            }
            const diagnosticsByName = diagnosticsWithOldMarkedAsStales.get(trimmedHardwareId);
            return diagnosticsByName?.get(name);
        });
        const nodesByLevel = getDiagnosticsByLevel(diagnosticsWithOldMarkedAsStales);
        const levels = Array.from(nodesByLevel.keys()).sort().reverse();
        const sortedNodes = sortByLevel
            ? [].concat(...levels.map((level) => filterAndSortDiagnostics(nodesByLevel.get(level) ?? [], hardwareIdFilter, pinnedIds)))
            : filterAndSortDiagnostics([].concat(...nodesByLevel.values()), hardwareIdFilter, pinnedIds);
        const nodes = [..._.compact(pinnedNodes), ...sortedNodes].filter(({ status }) => status.level >= minLevel);
        if (nodes.length === 0) {
            return ReactNull;
        }
        return (_jsx(AutoSizer, { children: ({ height, width }) => (_jsx(List, { width: width, height: height, style: { outline: "none" }, itemSize: 30, itemData: nodes, itemCount: nodes.length, overscanCount: 10, children: renderRow })) }));
    }, [
        diagnosticsWithOldMarkedAsStales,
        hardwareIdFilter,
        pinnedIds,
        renderRow,
        sortByLevel,
        minLevel,
        topicToRender,
    ]);
    const actionHandler = useCallback((action) => {
        if (action.action !== "update") {
            return;
        }
        const { path, value } = action.payload;
        saveConfig(produce((draft) => _.set(draft, path.slice(1), value)));
    }, [saveConfig]);
    useEffect(() => {
        updatePanelSettingsTree({
            actionHandler,
            nodes: buildSummarySettingsTree(config, topicToRender, availableTopics),
        });
    }, [actionHandler, availableTopics, config, topicToRender, updatePanelSettingsTree]);
    return (_jsxs(Stack, { flex: "auto", children: [_jsx(PanelToolbar, { children: _jsxs(Stack, { flex: "auto", direction: "row", gap: 1, children: [_jsx(Select, { className: classes.select, value: minLevel, id: "status-filter-menu", color: "secondary", size: "small", onChange: (event) => {
                                saveConfig({ minLevel: event.target.value });
                            }, MenuProps: { MenuListProps: { dense: true } }, children: KNOWN_LEVELS.map((level) => (_jsx(MenuItem, { value: level, children: _jsx(Typography, { variant: "inherit", color: MESSAGE_COLORS[LEVEL_NAMES[level] ?? "stale"], children: LEVEL_NAMES[level]?.toUpperCase() }) }, level))) }), _jsx(InputBase, { value: hardwareIdFilter, placeholder: "\u7B5B\u9009", onChange: (e) => {
                                saveConfig({ hardwareIdFilter: e.target.value });
                            }, style: { flex: "auto", font: "inherit" } })] }) }), _jsx(Stack, { flex: "auto", children: summary })] }));
}
const defaultConfig = {
    minLevel: 0,
    pinnedIds: [],
    hardwareIdFilter: "",
    topicToRender: "/diagnostics",
    sortByLevel: true,
};
export default Panel(Object.assign(DiagnosticSummary, {
    panelType: "DiagnosticSummary",
    defaultConfig,
}));
