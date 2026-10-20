import { jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { useState } from "react";
import { createStore } from "zustand";
import { EventsContext, } from "@foxglove/studio-base/context/EventsContext";
const NO_EVENTS = [];
function createEventsStore() {
    return createStore((set) => ({
        eventFetchCount: 0,
        events: { loading: false, value: NO_EVENTS },
        filter: "",
        selectedEventId: undefined,
        eventsSupported: false,
        deviceId: undefined,
        refreshEvents: () => {
            set((old) => ({ eventFetchCount: old.eventFetchCount + 1 }));
        },
        selectEvent: (id) => {
            set({ selectedEventId: id });
        },
        setEvents: (events) => {
            set({ events, selectedEventId: undefined });
        },
        setFilter: (filter) => {
            set({ filter });
        },
        // eslint-disable-next-line @foxglove/no-boolean-parameters
        setEventsSupported: (eventsSupported) => {
            set({ eventsSupported });
        },
        setDeviceId: (deviceId) => {
            set({ deviceId });
        },
    }));
}
export default function EventsProvider({ children }) {
    const [store] = useState(createEventsStore);
    return _jsx(EventsContext.Provider, { value: store, children: children });
}
