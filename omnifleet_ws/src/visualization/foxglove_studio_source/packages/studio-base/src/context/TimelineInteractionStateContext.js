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
import { createContext, useCallback } from "react";
import { useStore } from "zustand";
import { useGuaranteedContext } from "@foxglove/hooks";
export const TimelineInteractionStateContext = createContext(undefined);
const selectClearHoverValue = (store) => store.clearHoverValue;
export function useClearHoverValue() {
    return useTimelineInteractionState(selectClearHoverValue);
}
const selectSetHoverValue = (store) => {
    return store.setHoverValue;
};
export function useSetHoverValue() {
    return useTimelineInteractionState(selectSetHoverValue);
}
const undefinedSelector = () => undefined;
/**
 * Select the current hover value.
 *
 * By default this hook will return the latest hover value regardless of origin. Use options to
 * control when hover value updates cause the hook to return the updated value.
 *
 * @param componentId allow updates from hover values to those matching this componentId. If undefined, any component's hover values are returned.
 * @param disableUpdates disable any updates regardless of origin. If set the hook will not update with hover values even if other options would cause a match.
 * @param isPlaybackSeconds allow updates from hover values for PLAYBACK_SECONDS
 */
export function useHoverValue(opt) {
    const enabled = opt?.disableUpdates !== true;
    const componentId = opt?.componentId;
    const isPlaybackSeconds = opt?.isPlaybackSeconds ?? false;
    const selector = useCallback((store) => {
        if (store.hoverValue == undefined) {
            return undefined;
        }
        if (store.hoverValue.type === "PLAYBACK_SECONDS" && isPlaybackSeconds) {
            // Always show playback-time hover values for timestamp-based charts.
            return store.hoverValue;
        }
        // Otherwise only show hover bars when hovering over the component that set the hover value
        return componentId == undefined || store.hoverValue.componentId === componentId
            ? store.hoverValue
            : undefined;
    }, [componentId, isPlaybackSeconds]);
    return useTimelineInteractionState(enabled ? selector : undefinedSelector);
}
/**
 * This hook wraps all access to the interaction state store. Pass selectors
 * to access parts of the store.
 */
export function useTimelineInteractionState(selector) {
    const context = useGuaranteedContext(TimelineInteractionStateContext);
    return useStore(context, selector);
}
