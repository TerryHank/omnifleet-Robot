// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { createContext } from "react";
import { useStore } from "zustand";
import { useGuaranteedContext } from "@foxglove/hooks";
export const EventsContext = createContext(undefined);
export function useEvents(selector) {
    const context = useGuaranteedContext(EventsContext);
    return useStore(context, selector);
}
