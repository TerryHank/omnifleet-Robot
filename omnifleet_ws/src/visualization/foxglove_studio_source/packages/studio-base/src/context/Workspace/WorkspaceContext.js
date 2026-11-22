// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { createContext } from "react";
import { useStore } from "zustand";
import { useGuaranteedContext } from "@foxglove/hooks";
export const LeftSidebarItemKeys = ["panel-settings", "topics", "problems"];
export const RightSidebarItemKeys = [
    "events",
    "variables",
    "studio-logs-settings",
    "performance",
];
export const WorkspaceContext = createContext(undefined);
WorkspaceContext.displayName = "WorkspaceContext";
export const WorkspaceStoreSelectors = {
    selectPanelSettingsOpen: (store) => {
        return store.sidebars.left.open && store.sidebars.left.item === "panel-settings";
    },
};
/**
 * Fetches values from the workspace store.
 */
export function useWorkspaceStore(selector) {
    const context = useGuaranteedContext(WorkspaceContext);
    return useStore(context, selector);
}
