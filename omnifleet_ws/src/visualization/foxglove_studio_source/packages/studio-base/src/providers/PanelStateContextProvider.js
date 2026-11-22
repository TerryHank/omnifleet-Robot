import { jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { useCallback, useEffect, useState } from "react";
import { createStore } from "zustand";
import { usePanelContext } from "@foxglove/studio-base/components/PanelContext";
import { PanelStateContext, usePanelStateStore, } from "@foxglove/studio-base/context/PanelStateContext";
function createPanelStateStore(initialState) {
    return createStore((set) => {
        return {
            sequenceNumbers: {},
            settingsTrees: {},
            defaultTitles: {},
            incrementSequenceNumber: (panelId) => {
                set((state) => {
                    return {
                        sequenceNumbers: {
                            ...state.sequenceNumbers,
                            [panelId]: (state.sequenceNumbers[panelId] ?? 0) + 1,
                        },
                    };
                });
            },
            updateSettingsTree: (panelId, settingsTree) => {
                set((state) => ({
                    settingsTrees: {
                        ...state.settingsTrees,
                        [panelId]: settingsTree,
                    },
                }));
            },
            updateDefaultTitle: (panelId, defaultTitle) => {
                set((state) => ({ defaultTitles: { ...state.defaultTitles, [panelId]: defaultTitle } }));
            },
            ...initialState,
        };
    });
}
const updateSettingsTreeSelector = (store) => store.updateSettingsTree;
/**
 * Returns updater function for the current panels settings tree.
 */
export function usePanelSettingsTreeUpdate() {
    const { id } = usePanelContext();
    const updateStoreTree = usePanelStateStore(updateSettingsTreeSelector);
    const updateSettingsTree = useCallback((newTree) => {
        updateStoreTree(id, newTree);
    }, [id, updateStoreTree]);
    /** Cleanup unmounted panels
     * `actionHandler` can capture panel variables in closure context and keep them in memory
     * even after unmounting. To prevent this we set the panelSettingsTree entry to undefined,
     * allowing the actionHandler and its captured closure context from the unmounted panel to
     * be garbage collected.
     */
    useEffect(() => {
        return () => {
            updateStoreTree(id, undefined);
        };
    }, [id, updateStoreTree]);
    return updateSettingsTree;
}
const updateDefaultTitleSelector = (store) => store.updateDefaultTitle;
/**
 * Returns a [state, setState] pair that can be used to read and update a panel's default title.
 */
export function useDefaultPanelTitle() {
    const panelId = usePanelContext().id;
    const selector = useCallback((store) => store.defaultTitles[panelId], [panelId]);
    const updateDefaultTitle = usePanelStateStore(updateDefaultTitleSelector);
    const defaultTitle = usePanelStateStore(selector);
    const update = useCallback((newValue) => {
        updateDefaultTitle(panelId, newValue);
    }, [panelId, updateDefaultTitle]);
    return [defaultTitle, update];
}
export function PanelStateContextProvider(props) {
    const { children, initialState } = props;
    const [store] = useState(() => createPanelStateStore(initialState));
    return _jsx(PanelStateContext.Provider, { value: store, children: children });
}
