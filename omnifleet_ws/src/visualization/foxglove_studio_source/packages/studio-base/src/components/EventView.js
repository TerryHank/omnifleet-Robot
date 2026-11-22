import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { alpha } from "@mui/material";
import * as _ from "lodash-es";
import { Fragment } from "react";
import { makeStyles } from "tss-react/mui";
import { HighlightedText } from "@foxglove/studio-base/components/HighlightedText";
const useStyles = makeStyles()((theme, _params, classes) => ({
    spacer: {
        cursor: "default",
        height: theme.spacing(1),
        gridColumn: "span 2",
    },
    event: {
        display: "contents",
        cursor: "pointer",
        "&:hover": {
            [`.${classes.eventMetadata}`]: {
                backgroundColor: alpha(theme.palette.info.main, theme.palette.action.hoverOpacity),
                borderColor: theme.palette.info.main,
            },
        },
    },
    eventSelected: {
        [`.${classes.eventMetadata}`]: {
            backgroundColor: alpha(theme.palette.info.main, theme.palette.action.activatedOpacity),
            borderColor: theme.palette.info.main,
            boxShadow: `0 0 0 1px ${theme.palette.info.main}`,
        },
    },
    eventHovered: {
        [`.${classes.eventMetadata}`]: {
            backgroundColor: alpha(theme.palette.info.main, theme.palette.action.hoverOpacity),
            borderColor: theme.palette.info.main,
        },
    },
    eventMetadata: {
        padding: theme.spacing(1),
        backgroundColor: theme.palette.background.default,
        borderRight: `1px solid ${theme.palette.divider}`,
        borderBottom: `1px solid ${theme.palette.divider}`,
        "&:nth-of-type(odd)": {
            borderLeft: `1px solid ${theme.palette.divider}`,
        },
        "&:first-of-type": {
            borderTop: `1px solid ${theme.palette.divider}`,
            borderTopLeftRadius: theme.shape.borderRadius,
        },
        "&:nth-of-type(2)": {
            borderTop: `1px solid ${theme.palette.divider}`,
            borderTopRightRadius: theme.shape.borderRadius,
        },
        "&:nth-last-of-type(2)": {
            borderBottomRightRadius: theme.shape.borderRadius,
        },
        "&:nth-last-of-type(3)": {
            borderBottomLeftRadius: theme.shape.borderRadius,
        },
    },
}));
function formatEventDuration(event) {
    if (event.durationNanos === "0") {
        // instant
        return "-";
    }
    if (!event.durationNanos) {
        return "";
    }
    const intDuration = BigInt(event.durationNanos);
    if (intDuration >= BigInt(1e9)) {
        return `${Number(intDuration / BigInt(1e9))}s`;
    }
    if (intDuration >= BigInt(1e6)) {
        return `${Number(intDuration / BigInt(1e6))}ms`;
    }
    if (intDuration >= BigInt(1e3)) {
        return `${Number(intDuration / BigInt(1e3))}µs`;
    }
    return `${event.durationNanos}ns`;
}
function EventViewComponent(params) {
    const { event, filter, formattedTime, isHovered, isSelected, onClick, onHoverStart, onHoverEnd } = params;
    const { classes, cx } = useStyles();
    const fields = _.compact([
        ["start", formattedTime],
        Number(event.event.durationNanos) > 0 && ["duration", formatEventDuration(event.event)],
        ...Object.entries(event.event.metadata),
    ]);
    return (_jsxs("div", { "data-testid": "sidebar-event", className: cx(classes.event, {
            [classes.eventSelected]: isSelected,
            [classes.eventHovered]: isHovered,
        }), onClick: () => {
            onClick(event);
        }, onMouseEnter: () => {
            onHoverStart(event);
        }, onMouseLeave: () => {
            onHoverEnd(event);
        }, children: [fields.map(([key, value]) => (_jsxs(Fragment, { children: [_jsx("div", { className: classes.eventMetadata, children: _jsx(HighlightedText, { text: key ?? "", highlight: filter }) }), _jsx("div", { className: classes.eventMetadata, children: _jsx(HighlightedText, { text: value ?? "", highlight: filter }) })] }, key))), _jsx("div", { className: classes.spacer })] }));
}
export const EventView = React.memo(EventViewComponent);
