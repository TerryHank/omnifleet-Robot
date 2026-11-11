/// <reference types="react" />
import { StoreApi } from "zustand";
import { Immutable, SettingsTree } from "@foxglove/studio";
export type ImmutableSettingsTree = Immutable<SettingsTree>;
export type PanelStateStore = {
    /**
     * Used for forcing remounts on panels to make panels reload their saved configs. This is necessary
     * because panels are free to ignore updates to their config in the layout and maintain their own
     * internal state but we need some way of overriding this and forcing the panel to remount.
     */
    sequenceNumbers: Record<string, number>;
    /**
     * Per-panel settings UI trees.
     */
    settingsTrees: Record<string, ImmutableSettingsTree | undefined>;
    /** Per-panel default titles. */
    defaultTitles: Record<string, string | undefined>;
    /**
     * Increments the sequence number for the panel, forcing a remount.
     */
    incrementSequenceNumber: (panelId: string) => void;
    /**
     * Updates the settings UI for the given panel.
     */
    updateSettingsTree: (panelId: string, settingsTree: ImmutableSettingsTree | undefined) => void;
    /** Updates the default title for the given panel. */
    updateDefaultTitle: (panelId: string, title: string | undefined) => void;
};
export declare const PanelStateContext: import("react").Context<StoreApi<PanelStateStore> | undefined>;
export declare function usePanelStateStore<T>(selector: (store: PanelStateStore) => T): T;
