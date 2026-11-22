import { Fragment as _Fragment, jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { useLayoutEffect } from "react";
import { compare } from "@foxglove/rostime";
import { useMessagePipeline, } from "@foxglove/studio-base/components/MessagePipeline";
function activeDataSelector(ctx) {
    return ctx.playerState.activeData;
}
/**
 * RepeatAdapter handled looping from the start of playback when playback reaches the end
 *
 * NOTE: Because repeat adapter receives every message pipeline frame, we isolate its logic inside
 * a separate component so it does not cause virtual DOM diffing on any children.
 */
export function RepeatAdapter(props) {
    const { play, seek, repeatEnabled } = props;
    const activeData = useMessagePipeline(activeDataSelector);
    useLayoutEffect(() => {
        if (!repeatEnabled) {
            return;
        }
        const currentTime = activeData?.currentTime;
        const endTime = activeData?.endTime;
        const startTime = activeData?.startTime;
        // repeat logic could also live in messagePipeline but since it is only triggered
        // from playback controls we've implemented it here for now - if there is demand
        // to toggle repeat from elsewhere this logic can move
        if (startTime && currentTime && endTime && compare(currentTime, endTime) >= 0) {
            seek(startTime);
            // if the user turns on repeat and we are at the end, we assume they want to play from start
            // even if paused
            play();
        }
    }, [activeData, play, repeatEnabled, seek]);
    return _jsx(_Fragment, {});
}
