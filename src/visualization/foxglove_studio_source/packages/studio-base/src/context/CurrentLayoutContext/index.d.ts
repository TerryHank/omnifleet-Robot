/// <reference types="react" />
import { VariableValue, RenderState } from "@foxglove/studio";
import { PanelConfig, PlaybackConfig, UserScripts } from "@foxglove/studio-base/types/panels";
import { LayoutData, AddPanelPayload, ChangePanelLayoutPayload, ClosePanelPayload, CreateTabPanelPayload, DropPanelPayload, EndDragPayload, MoveTabPayload, SaveConfigsPayload, SplitPanelPayload, StartDragPayload, SwapPanelPayload } from "./actions";
type PanelType = string;
export type { LayoutData };
export type SharedPanelState = RenderState["sharedPanelState"];
export type SelectedLayout = {
    data: LayoutData | undefined;
    name?: string;
    edited?: boolean;
};
export type LayoutState = Readonly<{
    /**
     * Transient state shared between panels, keyed by panel type.
     */
    sharedPanelState?: Record<PanelType, SharedPanelState>;
    selectedLayout: SelectedLayout | undefined;
}>;
/**
 * Encapsulates the mosaic layout, user nodes, and playback settings (everything considered to be
 * part of a saved "layout") used by the current workspace.
 */
export interface ICurrentLayout {
    addLayoutStateListener: (listener: (_: LayoutState) => void) => void;
    removeLayoutStateListener: (listener: (_: LayoutState) => void) => void;
    addSelectedPanelIdsListener: (listener: (_: readonly string[]) => void) => void;
    removeSelectedPanelIdsListener: (listener: (_: readonly string[]) => void) => void;
    /**
     * We use the same mosaicId for all mosaics (at the top level and within tabs) to support
     * dragging and dropping between them.
     */
    mosaicId: string;
    getSelectedPanelIds: () => readonly string[];
    setSelectedPanelIds: (_: readonly string[] | ((prevState: readonly string[]) => readonly string[])) => void;
    actions: {
        /**
         * Returns the current state - useful for click handlers and callbacks that read the state
         * asynchronously and don't want to update every time the state changes.
         */
        getCurrentLayoutState: () => LayoutState;
        /**
         * Override any current layout. This will reset the layout state
         */
        setCurrentLayout: (newLayout: SelectedLayout | undefined) => void;
        /**
         * Update the transient state associated with a particular panel type.
         */
        updateSharedPanelState: (type: PanelType, data: SharedPanelState) => void;
        savePanelConfigs: (payload: SaveConfigsPayload) => void;
        updatePanelConfigs: (panelType: string, updater: (config: PanelConfig) => PanelConfig) => void;
        createTabPanel: (payload: CreateTabPanelPayload) => void;
        changePanelLayout: (payload: ChangePanelLayoutPayload) => void;
        overwriteGlobalVariables: (payload: Record<string, VariableValue>) => void;
        setGlobalVariables: (payload: Record<string, VariableValue>) => void;
        setUserScripts: (payload: Partial<UserScripts>) => void;
        setPlaybackConfig: (payload: Partial<PlaybackConfig>) => void;
        closePanel: (payload: ClosePanelPayload) => void;
        splitPanel: (payload: SplitPanelPayload) => void;
        swapPanel: (payload: SwapPanelPayload) => void;
        moveTab: (payload: MoveTabPayload) => void;
        addPanel: (payload: AddPanelPayload) => void;
        dropPanel: (payload: DropPanelPayload) => void;
        startDrag: (payload: StartDragPayload) => void;
        endDrag: (payload: EndDragPayload) => void;
    };
}
export type CurrentLayoutActions = ICurrentLayout["actions"];
export type SelectedPanelActions = {
    getSelectedPanelIds: () => readonly string[];
    selectedPanelIds: readonly string[];
    setSelectedPanelIds: (_: readonly string[] | ((prevState: readonly string[]) => string[])) => void;
    selectAllPanels: () => void;
    togglePanelSelected: (panelId: string, containingTabId: string | undefined) => void;
};
declare const CurrentLayoutContext: import("react").Context<ICurrentLayout | undefined>;
export declare function usePanelMosaicId(): string;
export declare function useCurrentLayoutActions(): CurrentLayoutActions;
export declare function useCurrentLayoutSelector<T>(selector: (layoutState: LayoutState) => T): T;
export declare function useSelectedPanels(): SelectedPanelActions;
export default CurrentLayoutContext;
