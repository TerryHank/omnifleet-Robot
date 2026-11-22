import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import ClearIcon from "@mui/icons-material/Clear";
import SearchIcon from "@mui/icons-material/Search";
import { AppBar, CircularProgress, IconButton, InputAdornment, TextField, Typography, } from "@mui/material";
import { useCallback, useMemo } from "react";
import { makeStyles } from "tss-react/mui";
import { useMessagePipeline, } from "@foxglove/studio-base/components/MessagePipeline";
import Stack from "@foxglove/studio-base/components/Stack";
import { useEvents, } from "@foxglove/studio-base/context/EventsContext";
import { useTimelineInteractionState, } from "@foxglove/studio-base/context/TimelineInteractionStateContext";
import { useAppTimeFormat } from "@foxglove/studio-base/hooks";
import { EventView } from "./EventView";
const useStyles = makeStyles()((theme) => ({
    appBar: {
        top: -1,
        zIndex: theme.zIndex.appBar - 1,
        display: "flex",
        flexDirection: "row",
        padding: theme.spacing(1),
        gap: theme.spacing(1),
        alignItems: "center",
        borderBottom: `1px solid ${theme.palette.divider}`,
    },
    grid: {
        display: "grid",
        flexShrink: 1,
        gridTemplateColumns: "auto 1fr",
        overflowY: "auto",
        padding: theme.spacing(1),
    },
    root: {
        backgroundColor: theme.palette.background.paper,
        maxHeight: "100%",
    },
}));
const selectSeek = (ctx) => ctx.seekPlayback;
const selectEventFilter = (store) => store.filter;
const selectSetEventFilter = (store) => store.setFilter;
const selectEvents = (store) => store.events;
const selectHoveredEvent = (store) => store.hoveredEvent;
const selectSetHoveredEvent = (store) => store.setHoveredEvent;
const selectEventsAtHoverValue = (store) => store.eventsAtHoverValue;
const selectSelectedEventId = (store) => store.selectedEventId;
const selectSelectEvent = (store) => store.selectEvent;
export function EventsList() {
    const events = useEvents(selectEvents);
    const selectedEventId = useEvents(selectSelectedEventId);
    const selectEvent = useEvents(selectSelectEvent);
    const { formatTime } = useAppTimeFormat();
    const seek = useMessagePipeline(selectSeek);
    const eventsAtHoverValue = useTimelineInteractionState(selectEventsAtHoverValue);
    const hoveredEvent = useTimelineInteractionState(selectHoveredEvent);
    const setHoveredEvent = useTimelineInteractionState(selectSetHoveredEvent);
    const filter = useEvents(selectEventFilter);
    const setFilter = useEvents(selectSetEventFilter);
    const timestampedEvents = useMemo(() => (events.value ?? []).map((event) => {
        return { ...event, formattedTime: formatTime(event.event.startTime) };
    }), [events, formatTime]);
    const clearFilter = useCallback(() => {
        setFilter("");
    }, [setFilter]);
    const onClick = useCallback((event) => {
        if (event.event.id === selectedEventId) {
            selectEvent(undefined);
        }
        else {
            selectEvent(event.event.id);
        }
        if (seek) {
            seek(event.event.startTime);
        }
    }, [seek, selectEvent, selectedEventId]);
    const onHoverEnd = useCallback(() => {
        setHoveredEvent(undefined);
    }, [setHoveredEvent]);
    const onHoverStart = useCallback((event) => {
        setHoveredEvent(event);
    }, [setHoveredEvent]);
    const { classes } = useStyles();
    return (_jsxs(Stack, { className: classes.root, fullHeight: true, children: [_jsx(AppBar, { className: classes.appBar, position: "sticky", color: "inherit", elevation: 0, children: _jsx(TextField, { variant: "filled", fullWidth: true, size: "small", value: filter, onChange: (event) => {
                        setFilter(event.currentTarget.value);
                    }, placeholder: "Search by key, value, or key:value", InputProps: {
                        startAdornment: (_jsx(InputAdornment, { position: "start", children: _jsx(SearchIcon, { fontSize: "small" }) })),
                        endAdornment: filter !== "" && (_jsx(IconButton, { edge: "end", onClick: clearFilter, size: "small", children: _jsx(ClearIcon, { fontSize: "small" }) })),
                    } }) }), events.loading && (_jsx(Stack, { flex: "auto", padding: 2, fullHeight: true, alignItems: "center", justifyContent: "center", children: _jsx(CircularProgress, {}) })), events.error && (_jsx(Stack, { flex: "auto", padding: 2, fullHeight: true, alignItems: "center", justifyContent: "center", children: _jsx(Typography, { align: "center", color: "error", children: "Error loading events." }) })), events.value && events.value.length === 0 && (_jsx(Stack, { flex: "auto", padding: 2, fullHeight: true, alignItems: "center", justifyContent: "center", children: _jsx(Typography, { align: "center", color: "text.secondary", children: "No Events" }) })), _jsx("div", { className: classes.grid, children: timestampedEvents.map((event) => {
                    return (_jsx(EventView, { event: event, filter: filter, formattedTime: event.formattedTime, 
                        // When hovering within the event list only show hover state on directly
                        // hovered event.
                        isHovered: hoveredEvent
                            ? event.event.id === hoveredEvent.event.id
                            : eventsAtHoverValue[event.event.id] != undefined, isSelected: event.event.id === selectedEventId, onClick: onClick, onHoverStart: onHoverStart, onHoverEnd: onHoverEnd }, event.event.id));
                }) })] }));
}
