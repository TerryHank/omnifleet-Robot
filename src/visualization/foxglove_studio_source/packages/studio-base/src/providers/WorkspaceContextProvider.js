import { jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import * as _ from "lodash-es";
import { useState } from "react";
import { createStore } from "zustand";
import { persist } from "zustand/middleware";
import { WorkspaceContext, } from "@foxglove/studio-base/context/Workspace/WorkspaceContext";
import { migrateV0WorkspaceState } from "@foxglove/studio-base/context/Workspace/migrations";
/**
 * Creates the default initial state for the workspace store.
 */
export function makeWorkspaceContextInitialState() {
    return {
        dialogs: {
            dataSource: {
                activeDataSource: undefined,
                item: undefined,
                open: false,
            },
            preferences: {
                initialTab: undefined,
                open: false,
            },
        },
        featureTours: {
            active: undefined,
            shown: [],
        },
        sidebars: {
            left: {
                item: "panel-settings",
                open: true,
                size: undefined,
            },
            right: {
                item: undefined,
                open: false,
                size: undefined,
            },
        },
        playbackControls: {
            repeat: false,
        },
    };
}
function createWorkspaceContextStore(initialState, options) {
    const stateCreator = () => {
        const store = {
            ...makeWorkspaceContextInitialState(),
            ...initialState,
        };
        return store;
    };
    if (options?.disablePersistenceForStorybook === true) {
        return createStore()(stateCreator);
    }
    return createStore()(persist(stateCreator, {
        name: "fox.workspace",
        version: 1,
        migrate: migrateV0WorkspaceState,
        partialize: (state) => {
            // Note that this is an opt-in list of keys from the store that we
            // include and restore when persisting to and from localStorage.
            return _.pick(state, ["featureTours", "playbackControls", "sidebars"]);
        },
    }));
}
export default function WorkspaceContextProvider(props) {
    const { children, initialState, workspaceStoreCreator, disablePersistenceForStorybook } = props;
    const [store] = useState(() => workspaceStoreCreator
        ? workspaceStoreCreator(initialState, { disablePersistenceForStorybook })
        : createWorkspaceContextStore(initialState, { disablePersistenceForStorybook }));
    return _jsx(WorkspaceContext.Provider, { value: store, children: children });
}
