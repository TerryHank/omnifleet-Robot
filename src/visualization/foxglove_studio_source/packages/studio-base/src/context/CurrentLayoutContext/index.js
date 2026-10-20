// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { createContext, useCallback, useLayoutEffect, useReducer, useRef, useState } from "react";
import { getLeaves } from "react-mosaic-component";
import { useShallowMemo, selectWithUnstableIdentityWarning, useGuaranteedContext, } from "@foxglove/hooks";
import Logger from "@foxglove/log";
import useShouldNotChangeOften from "@foxglove/studio-base/hooks/useShouldNotChangeOften";
import toggleSelectedPanel from "@foxglove/studio-base/providers/CurrentLayoutProvider/toggleSelectedPanel";
const log = Logger.getLogger(__filename);
const CurrentLayoutContext = createContext(undefined);
CurrentLayoutContext.displayName = "CurrentLayoutContext";
export function usePanelMosaicId() {
    return useGuaranteedContext(CurrentLayoutContext).mosaicId;
}
export function useCurrentLayoutActions() {
    return useGuaranteedContext(CurrentLayoutContext).actions;
}
export function useCurrentLayoutSelector(selector) {
    const currentLayout = useGuaranteedContext(CurrentLayoutContext);
    const [, forceUpdate] = useReducer((x) => x + 1, 0);
    // Catch locations using unstable function selectors
    useShouldNotChangeOften(selector, () => {
        log.warn("useCurrentLayoutSelector is changing frequently. Rewrite your selector as a stable function.");
    });
    const state = useRef(undefined);
    if (!state.current || selector !== state.current.selector) {
        state.current = {
            value: selectWithUnstableIdentityWarning(currentLayout.actions.getCurrentLayoutState(), selector),
            selector,
        };
    }
    useLayoutEffect(() => {
        let mounted = true;
        const listener = (layoutState) => {
            // Note: Our removeLayoutStateListener is is too late if the layout state listeners are already
            // being invoked. Our component might become unmounted during the state listener invocation
            if (!mounted) {
                return;
            }
            const newValue = selectWithUnstableIdentityWarning(layoutState, selector);
            if (newValue === state.current?.value) {
                return;
            }
            state.current = {
                value: newValue,
                selector,
            };
            forceUpdate();
        };
        // Update if necessary, i.e. if the state has changed between render and this effect
        listener(currentLayout.actions.getCurrentLayoutState());
        currentLayout.addLayoutStateListener(listener);
        return () => {
            mounted = false;
            currentLayout.removeLayoutStateListener(listener);
        };
    }, [currentLayout, selector]);
    return state.current.value;
}
export function useSelectedPanels() {
    const currentLayout = useGuaranteedContext(CurrentLayoutContext);
    const [selectedPanelIds, setSelectedPanelIdsState] = useState(() => currentLayout.getSelectedPanelIds());
    useLayoutEffect(() => {
        const listener = (newIds) => {
            setSelectedPanelIdsState(newIds);
        };
        currentLayout.addSelectedPanelIdsListener(listener);
        return () => {
            currentLayout.removeSelectedPanelIdsListener(listener);
        };
    }, [currentLayout]);
    const setSelectedPanelIds = useGuaranteedContext(CurrentLayoutContext).setSelectedPanelIds;
    const getSelectedPanelIds = useGuaranteedContext(CurrentLayoutContext).getSelectedPanelIds;
    const { getCurrentLayoutState: getCurrentLayout } = useCurrentLayoutActions();
    const selectAllPanels = useCallback(() => {
        // eslint-disable-next-line no-restricted-syntax
        const panelIds = getLeaves(getCurrentLayout().selectedLayout?.data?.layout ?? null);
        setSelectedPanelIds(panelIds);
    }, [getCurrentLayout, setSelectedPanelIds]);
    const togglePanelSelected = useCallback((panelId, containingTabId) => {
        setSelectedPanelIds((selectedIds) => {
            const { selectedLayout } = getCurrentLayout();
            if (!selectedLayout?.data) {
                return selectedIds;
            }
            return toggleSelectedPanel(panelId, containingTabId, selectedLayout.data.configById, selectedIds);
        });
    }, [setSelectedPanelIds, getCurrentLayout]);
    return useShallowMemo({
        getSelectedPanelIds,
        selectedPanelIds,
        setSelectedPanelIds,
        selectAllPanels,
        togglePanelSelected,
    });
}
export default CurrentLayoutContext;
