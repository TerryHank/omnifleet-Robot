import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { Fade, Tooltip } from "@mui/material";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useLatest } from "react-use";
import { makeStyles } from "tss-react/mui";
import { v4 as uuidv4 } from "uuid";
import { subtract as subtractTimes, add as addTimes, toSec, fromSec, } from "@foxglove/rostime";
import { useMessagePipeline, } from "@foxglove/studio-base/components/MessagePipeline";
import Stack from "@foxglove/studio-base/components/Stack";
import { useClearHoverValue, useSetHoverValue, } from "@foxglove/studio-base/context/TimelineInteractionStateContext";
import { PlayerPresence } from "@foxglove/studio-base/players/types";
import { EventsOverlay } from "./EventsOverlay";
import PlaybackBarHoverTicks from "./PlaybackBarHoverTicks";
import { PlaybackControlsTooltipContent } from "./PlaybackControlsTooltipContent";
import { ProgressPlot } from "./ProgressPlot";
import Slider from "./Slider";
const useStyles = makeStyles()((theme) => ({
    marker: {
        backgroundColor: theme.palette.text.primary,
        position: "absolute",
        height: 16,
        borderRadius: 1,
        width: 2,
        transform: "translate(-50%, 0)",
    },
    track: {
        position: "absolute",
        left: 0,
        right: 0,
        height: 6,
        backgroundColor: theme.palette.action.focus,
    },
    trackDisabled: {
        opacity: theme.palette.action.disabledOpacity,
    },
}));
const selectStartTime = (ctx) => ctx.playerState.activeData?.startTime;
const selectCurrentTime = (ctx) => ctx.playerState.activeData?.currentTime;
const selectEndTime = (ctx) => ctx.playerState.activeData?.endTime;
const selectRanges = (ctx) => ctx.playerState.progress.fullyLoadedFractionRanges;
const selectPresence = (ctx) => ctx.playerState.presence;
export default function Scrubber(props) {
    const { onSeek } = props;
    const { classes, cx } = useStyles();
    const [hoverComponentId] = useState(() => uuidv4());
    const startTime = useMessagePipeline(selectStartTime);
    const currentTime = useMessagePipeline(selectCurrentTime);
    const endTime = useMessagePipeline(selectEndTime);
    const presence = useMessagePipeline(selectPresence);
    const ranges = useMessagePipeline(selectRanges);
    const setHoverValue = useSetHoverValue();
    const [hoverInfo, setHoverInfo] = useState();
    const latestHoverInfo = useLatest(hoverInfo);
    const latestStartTime = useLatest(startTime);
    const latestEndTime = useLatest(endTime);
    const onChange = useCallback((fraction) => {
        if (!latestStartTime.current || !latestEndTime.current) {
            return;
        }
        onSeek(addTimes(latestStartTime.current, fromSec(fraction * toSec(subtractTimes(latestEndTime.current, latestStartTime.current)))));
    }, [onSeek, latestEndTime, latestStartTime]);
    const onHoverOver = useCallback(({ fraction, clientX, clientY }) => {
        if (!latestStartTime.current || !latestEndTime.current) {
            return;
        }
        const duration = toSec(subtractTimes(latestEndTime.current, latestStartTime.current));
        const timeFromStart = fromSec(fraction * duration);
        setHoverInfo({ stamp: addTimes(latestStartTime.current, timeFromStart), clientX, clientY });
        setHoverValue({
            componentId: hoverComponentId,
            type: "PLAYBACK_SECONDS",
            value: toSec(timeFromStart),
        });
    }, [hoverComponentId, latestEndTime, latestStartTime, setHoverValue]);
    const clearHoverValue = useClearHoverValue();
    const onHoverOut = useCallback(() => {
        clearHoverValue(hoverComponentId);
        setHoverInfo(undefined);
    }, [clearHoverValue, hoverComponentId]);
    // Clean up the hover value when we are unmounted -- important for storybook.
    useEffect(() => onHoverOut, [onHoverOut]);
    const renderSlider = useCallback((val) => {
        if (val == undefined) {
            return undefined;
        }
        return _jsx("div", { className: classes.marker, style: { left: `${val * 100}%` } });
    }, [classes.marker]);
    const min = startTime && toSec(startTime);
    const max = endTime && toSec(endTime);
    const fraction = currentTime && startTime && endTime
        ? toSec(subtractTimes(currentTime, startTime)) / toSec(subtractTimes(endTime, startTime))
        : undefined;
    const loading = presence === PlayerPresence.INITIALIZING || presence === PlayerPresence.BUFFERING;
    const popperRef = React.useRef(ReactNull);
    const isHovered = hoverInfo != undefined;
    const popperProps = useMemo(() => ({
        open: isHovered, // Keep the tooltip visible while dragging even when the mouse is outside the playback bar
        popperRef,
        modifiers: [
            {
                name: "computeStyles",
                options: {
                    gpuAcceleration: false, // Fixes hairline seam on arrow in chrome.
                },
            },
            {
                name: "offset",
                options: {
                    // Offset popper to hug the track better.
                    offset: [0, 4],
                },
            },
        ],
        anchorEl: {
            getBoundingClientRect: () => {
                return new DOMRect(latestHoverInfo.current?.clientX ?? 0, latestHoverInfo.current?.clientY ?? 0, 0, 0);
            },
        },
    }), [isHovered, latestHoverInfo]);
    useEffect(() => {
        if (popperRef.current != undefined) {
            void popperRef.current.update();
        }
    }, [hoverInfo]);
    return (_jsx(Tooltip, { title: hoverInfo != undefined ? _jsx(PlaybackControlsTooltipContent, { stamp: hoverInfo.stamp }) : "", placement: "top", disableInteractive: true, TransitionComponent: Fade, TransitionProps: { timeout: 0 }, PopperProps: popperProps, children: _jsxs(Stack, { direction: "row", flexGrow: 1, alignItems: "center", position: "relative", style: { height: 32 }, children: [_jsx("div", { className: cx(classes.track, { [classes.trackDisabled]: !startTime }) }), _jsx(Stack, { position: "absolute", flex: "auto", fullWidth: true, style: { height: 6 }, children: _jsx(ProgressPlot, { loading: loading, availableRanges: ranges }) }), _jsx(Stack, { fullHeight: true, fullWidth: true, position: "absolute", flex: 1, children: _jsx(Slider, { disabled: min == undefined || max == undefined, fraction: fraction, onHoverOver: onHoverOver, onHoverOut: onHoverOut, onChange: onChange, renderSlider: renderSlider }) }), _jsx(EventsOverlay, {}), _jsx(PlaybackBarHoverTicks, { componentId: hoverComponentId })] }) }));
}
