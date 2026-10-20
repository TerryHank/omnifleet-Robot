import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import * as _ from "lodash-es";
import { useCallback, useMemo, useRef, useState } from "react";
import { getNodeAtPath } from "react-mosaic-component";
import shallowequal from "shallowequal";
import { v4 as uuidv4 } from "uuid";
import { useShallowMemo } from "@foxglove/hooks";
import Logger from "@foxglove/log";
import { useAnalytics } from "@foxglove/studio-base/context/AnalyticsContext";
import CurrentLayoutContext from "@foxglove/studio-base/context/CurrentLayoutContext";
import panelsReducer from "@foxglove/studio-base/providers/CurrentLayoutProvider/reducers";
import { AppEvent } from "@foxglove/studio-base/services/IAnalytics";
import { getPanelTypeFromId } from "@foxglove/studio-base/util/layout";
import { IncompatibleLayoutVersionAlert } from "./IncompatibleLayoutVersionAlert";
const log = Logger.getLogger(__filename);
export const MAX_SUPPORTED_LAYOUT_VERSION = 1;
/**
 * Concrete implementation of CurrentLayoutContext.Provider which handles
 * automatically restoring the current layout from LayoutStorage.
 */
export default function CurrentLayoutProvider({ children }) {
    const analytics = useAnalytics();
    const [mosaicId] = useState(() => uuidv4());
    const layoutStateListeners = useRef(new Set());
    const addLayoutStateListener = useCallback((listener) => {
        layoutStateListeners.current.add(listener);
    }, []);
    const removeLayoutStateListener = useCallback((listener) => {
        layoutStateListeners.current.delete(listener);
    }, []);
    const [layoutState, setLayoutStateInternal] = useState({
        selectedLayout: undefined,
    });
    const layoutStateRef = useRef(layoutState);
    const [incompatibleLayoutVersionError, setIncompatibleLayoutVersionError] = useState(false);
    const setLayoutState = useCallback((newState) => {
        const layoutVersion = newState.selectedLayout?.data?.version;
        if (layoutVersion != undefined && layoutVersion > MAX_SUPPORTED_LAYOUT_VERSION) {
            setIncompatibleLayoutVersionError(true);
            setLayoutStateInternal({ selectedLayout: undefined });
            return;
        }
        setLayoutStateInternal(newState);
        // listeners rely on being able to getCurrentLayoutState() inside effects that may run before we re-render
        layoutStateRef.current = newState;
        for (const listener of [...layoutStateListeners.current]) {
            listener(newState);
        }
    }, []);
    const selectedPanelIds = useRef([]);
    const selectedPanelIdsListeners = useRef(new Set());
    const addSelectedPanelIdsListener = useCallback((listener) => {
        selectedPanelIdsListeners.current.add(listener);
    }, []);
    const removeSelectedPanelIdsListener = useCallback((listener) => {
        selectedPanelIdsListeners.current.delete(listener);
    }, []);
    const getSelectedPanelIds = useCallback(() => selectedPanelIds.current, []);
    const setSelectedPanelIds = useCallback((value) => {
        const newValue = typeof value === "function" ? value(selectedPanelIds.current) : value;
        if (!shallowequal(newValue, selectedPanelIds.current)) {
            selectedPanelIds.current = newValue;
            for (const listener of [...selectedPanelIdsListeners.current]) {
                listener(selectedPanelIds.current);
            }
        }
    }, []);
    const performAction = useCallback((action) => {
        if (layoutStateRef.current.selectedLayout?.data == undefined) {
            return;
        }
        const oldData = layoutStateRef.current.selectedLayout.data;
        const newData = panelsReducer(oldData, action);
        // The panel state did not change, so no need to perform layout state
        // updates or layout manager updates.
        if (_.isEqual(oldData, newData)) {
            log.warn("Panel action resulted in identical config:", action);
            return;
        }
        // Get all the panel types that exist in the new config
        const panelTypesInUse = _.uniq(Object.keys(newData.configById).map(getPanelTypeFromId));
        setLayoutState({
            // discared shared panel state for panel types that are no longer in the layout
            sharedPanelState: _.pick(layoutStateRef.current.sharedPanelState, panelTypesInUse),
            selectedLayout: {
                data: newData,
                name: layoutStateRef.current.selectedLayout.name,
                edited: true,
            },
        });
    }, [setLayoutState]);
    const setCurrentLayout = useCallback((newLayout) => {
        setLayoutState({
            sharedPanelState: {},
            selectedLayout: newLayout,
        });
    }, [setLayoutState]);
    const updateSharedPanelState = useCallback((type, newSharedState) => {
        if (layoutStateRef.current.selectedLayout?.data == undefined) {
            return;
        }
        setLayoutState({
            ...layoutStateRef.current,
            sharedPanelState: { ...layoutStateRef.current.sharedPanelState, [type]: newSharedState },
        });
    }, [setLayoutState]);
    const actions = useMemo(() => ({
        getCurrentLayoutState: () => layoutStateRef.current,
        setCurrentLayout,
        updateSharedPanelState,
        savePanelConfigs: (payload) => {
            performAction({ type: "SAVE_PANEL_CONFIGS", payload });
        },
        updatePanelConfigs: (panelType, perPanelFunc) => {
            performAction({ type: "SAVE_FULL_PANEL_CONFIG", payload: { panelType, perPanelFunc } });
        },
        createTabPanel: (payload) => {
            performAction({ type: "CREATE_TAB_PANEL", payload });
            setSelectedPanelIds([]);
            void analytics.logEvent(AppEvent.PANEL_ADD, { type: "Tab" });
        },
        changePanelLayout: (payload) => {
            performAction({ type: "CHANGE_PANEL_LAYOUT", payload });
        },
        overwriteGlobalVariables: (payload) => {
            performAction({ type: "OVERWRITE_GLOBAL_DATA", payload });
        },
        setGlobalVariables: (payload) => {
            performAction({ type: "SET_GLOBAL_DATA", payload });
        },
        setUserScripts: (payload) => {
            performAction({ type: "SET_USER_NODES", payload });
        },
        setPlaybackConfig: (payload) => {
            performAction({ type: "SET_PLAYBACK_CONFIG", payload });
        },
        closePanel: (payload) => {
            performAction({ type: "CLOSE_PANEL", payload });
            const closedId = getNodeAtPath(payload.root, payload.path);
            // Deselect the removed panel
            setSelectedPanelIds((ids) => ids.filter((id) => id !== closedId));
            void analytics.logEvent(AppEvent.PANEL_DELETE, typeof closedId === "string" ? { type: getPanelTypeFromId(closedId) } : undefined);
        },
        splitPanel: (payload) => {
            performAction({ type: "SPLIT_PANEL", payload });
        },
        swapPanel: (payload) => {
            // Select the new panel if the original panel was selected. We don't know what
            // the new panel id will be so we diff the panelIds of the old and
            // new layout so we can select the new panel.
            const originalIsSelected = selectedPanelIds.current.includes(payload.originalId);
            const beforePanelIds = Object.keys(layoutStateRef.current.selectedLayout?.data?.configById ?? {});
            performAction({ type: "SWAP_PANEL", payload });
            if (originalIsSelected) {
                const afterPanelIds = Object.keys(layoutStateRef.current.selectedLayout?.data?.configById ?? {});
                setSelectedPanelIds(_.difference(afterPanelIds, beforePanelIds));
            }
            void analytics.logEvent(AppEvent.PANEL_ADD, { type: payload.type, action: "swap" });
            void analytics.logEvent(AppEvent.PANEL_DELETE, {
                type: getPanelTypeFromId(payload.originalId),
                action: "swap",
            });
        },
        moveTab: (payload) => {
            performAction({ type: "MOVE_TAB", payload });
        },
        addPanel: (payload) => {
            performAction({ type: "ADD_PANEL", payload });
            void analytics.logEvent(AppEvent.PANEL_ADD, { type: getPanelTypeFromId(payload.id) });
        },
        dropPanel: (payload) => {
            performAction({ type: "DROP_PANEL", payload });
            void analytics.logEvent(AppEvent.PANEL_ADD, {
                type: payload.newPanelType,
                action: "drop",
            });
        },
        startDrag: (payload) => {
            performAction({ type: "START_DRAG", payload });
        },
        endDrag: (payload) => {
            performAction({ type: "END_DRAG", payload });
        },
    }), [analytics, performAction, setCurrentLayout, setSelectedPanelIds, updateSharedPanelState]);
    const value = useShallowMemo({
        addLayoutStateListener,
        removeLayoutStateListener,
        addSelectedPanelIdsListener,
        removeSelectedPanelIdsListener,
        mosaicId,
        getSelectedPanelIds,
        setSelectedPanelIds,
        actions,
    });
    return (_jsxs(CurrentLayoutContext.Provider, { value: value, children: [children, incompatibleLayoutVersionError && (_jsx(IncompatibleLayoutVersionAlert, { onClose: () => {
                    setIncompatibleLayoutVersionError(false);
                } }))] }));
}
