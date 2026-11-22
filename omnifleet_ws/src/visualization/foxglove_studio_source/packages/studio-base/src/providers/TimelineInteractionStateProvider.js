import { jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import * as _ from "lodash-es";
import { useState } from "react";
import { createStore } from "zustand";
import { TimelineInteractionStateContext, } from "@foxglove/studio-base/context/TimelineInteractionStateContext";
function createTimelineInteractionStateStore() {
    return createStore((set) => {
        return {
            eventsAtHoverValue: {},
            globalBounds: undefined,
            hoveredEvent: undefined,
            hoverValue: undefined,
            clearHoverValue: (componentId) => {
                set((store) => ({
                    hoverValue: store.hoverValue?.componentId === componentId ? undefined : store.hoverValue,
                }));
            },
            setEventsAtHoverValue: (eventsAtHoverValue) => {
                set({ eventsAtHoverValue: _.keyBy(eventsAtHoverValue, (event) => event.event.id) });
            },
            setGlobalBounds: (newBounds) => {
                if (typeof newBounds === "function") {
                    set((store) => ({ globalBounds: newBounds(store.globalBounds) }));
                }
                else {
                    set({ globalBounds: newBounds });
                }
            },
            setHoveredEvent: (hoveredEvent) => {
                if (hoveredEvent) {
                    set({
                        hoveredEvent,
                        hoverValue: {
                            componentId: `event_${hoveredEvent.event.id}`,
                            type: "PLAYBACK_SECONDS",
                            value: hoveredEvent.secondsSinceStart,
                        },
                    });
                }
                else {
                    set({ hoveredEvent: undefined, hoverValue: undefined });
                }
            },
            setHoverValue: (newValue) => {
                set((store) => ({
                    hoverValue: _.isEqual(newValue, store.hoverValue) ? store.hoverValue : newValue,
                }));
            },
        };
    });
}
export default function TimelineInteractionStateProvider({ children, }) {
    const [store] = useState(createTimelineInteractionStateStore());
    return (_jsx(TimelineInteractionStateContext.Provider, { value: store, children: children }));
}
