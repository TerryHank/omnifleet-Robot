// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { createContext } from "react";
import { useStore } from "zustand";
import { useGuaranteedContext } from "@foxglove/hooks";
export const ProblemsContext = createContext(undefined);
ProblemsContext.displayName = "ProblemsContext";
/**
 * Fetches values from the problems store.
 */
export function useProblemsStore(selector) {
    const context = useGuaranteedContext(ProblemsContext);
    return useStore(context, selector);
}
const selectActions = (store) => store.actions;
/**
 * Convenience hook for accessing problems store actions.
 */
export function useProblemsActions() {
    return useProblemsStore(selectActions);
}
