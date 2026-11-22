import { jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { alpha } from "@mui/material";
import * as _ from "lodash-es";
import { makeStyles } from "tss-react/mui";
import { useEvents, } from "@foxglove/studio-base/context/EventsContext";
import { useTimelineInteractionState, } from "@foxglove/studio-base/context/TimelineInteractionStateContext";
const useStyles = makeStyles()(({ transitions, palette }) => ({
    root: {
        inset: 0,
        pointerEvents: "none",
        position: "absolute",
        display: "flex",
        alignItems: "center",
    },
    tick: {
        transition: transitions.create("height", { duration: transitions.duration.shortest }),
        backgroundBlendMode: "overlay",
        backgroundColor: alpha(palette.info.main, 0.58),
        position: "absolute",
        height: 6,
    },
    tickHovered: {
        transition: transitions.create("height", { duration: transitions.duration.shortest }),
        backgroundColor: alpha(palette.info.main, 0.58),
        border: `1px solid ${palette.info.main}`,
        height: 12,
    },
    tickSelected: {
        transition: transitions.create("height", {
            duration: transitions.duration.shortest,
        }),
        backgroundColor: alpha(palette.info.main, 0.67),
        height: 12,
    },
}));
const selectEvents = (store) => store.events;
const selectHoveredEvent = (store) => store.hoveredEvent;
const selectEventsAtHoverValue = (store) => store.eventsAtHoverValue;
const selectSelectedEventId = (store) => store.selectedEventId;
function EventTick({ event }) {
    const eventsAtHoverValue = useTimelineInteractionState(selectEventsAtHoverValue);
    const hoveredEvent = useTimelineInteractionState(selectHoveredEvent);
    const selectedEventId = useEvents(selectSelectedEventId);
    const { classes, cx } = useStyles();
    const left = `calc(${_.clamp(event.startPosition, 0, 1) * 100}% - 1px)`;
    const right = `calc(100% - ${_.clamp(event.endPosition, 0, 1) * 100}% - 1px)`;
    return (_jsx("div", { className: cx(classes.tick, {
            [classes.tickHovered]: hoveredEvent
                ? event.event.id === hoveredEvent.event.id
                : eventsAtHoverValue[event.event.id] != undefined,
            [classes.tickSelected]: selectedEventId === event.event.id,
        }), style: { left, right } }));
}
const MemoEventTick = React.memo(EventTick);
export function EventsOverlay() {
    const events = useEvents(selectEvents);
    const { classes } = useStyles();
    return (_jsx("div", { className: classes.root, children: (events.value ?? []).map((event) => (_jsx(MemoEventTick, { event: event }, event.event.id))) }));
}
