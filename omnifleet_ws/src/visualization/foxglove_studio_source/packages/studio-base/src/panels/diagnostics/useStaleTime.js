// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { useCallback, useEffect, useMemo, useState } from "react";
import { clampTime, subtract } from "@foxglove/rostime";
import { useMessagePipeline, useMessagePipelineGetter, } from "@foxglove/studio-base/components/MessagePipeline";
const DEFAULT_UPDATE_INTERVAL_MS = 1000;
const selectLastSeekTime = (ctx) => ctx.playerState.activeData?.lastSeekTime;
// Returns a time which specifies from when diagnostic messages are considered stale.
export default function useStaleTime(secondsUntilStale, updateIntervalMillis) {
    const messagePipeline = useMessagePipelineGetter();
    const getCurrentTime = useCallback(() => {
        const { playerState } = messagePipeline();
        return playerState.activeData?.currentTime;
    }, [messagePipeline]);
    const [currentTime, setCurrentTime] = useState(() => getCurrentTime());
    useEffect(() => {
        const interval = setInterval(() => {
            setCurrentTime(getCurrentTime());
        }, updateIntervalMillis ?? DEFAULT_UPDATE_INTERVAL_MS);
        return () => {
            clearInterval(interval);
        };
    }, [getCurrentTime, updateIntervalMillis]);
    const lastSeekTime = useMessagePipeline(selectLastSeekTime);
    useEffect(() => {
        setCurrentTime(getCurrentTime());
    }, [getCurrentTime, lastSeekTime]);
    return useMemo(() => {
        const timeUntilStale = { sec: Math.floor(secondsUntilStale), nsec: 0 };
        return currentTime && secondsUntilStale >= 1
            ? subtract(clampTime(currentTime, timeUntilStale, currentTime), timeUntilStale)
            : undefined;
    }, [currentTime, secondsUntilStale]);
}
