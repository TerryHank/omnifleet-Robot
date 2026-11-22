/// <reference types="react" />
import { StoreApi } from "zustand";
import { AppSettingsTab } from "@foxglove/studio-base/components/AppSettingsDialog/AppSettingsDialog";
import { DataSourceDialogItem } from "@foxglove/studio-base/components/DataSourceDialog";
import { IDataSourceFactory } from "@foxglove/studio-base/context/PlayerSelectionContext";
export declare const LeftSidebarItemKeys: readonly ["panel-settings", "topics", "problems"];
export type LeftSidebarItemKey = (typeof LeftSidebarItemKeys)[number];
export declare const RightSidebarItemKeys: readonly ["events", "variables", "studio-logs-settings", "performance"];
export type RightSidebarItemKey = (typeof RightSidebarItemKeys)[number];
export type WorkspaceContextStore = {
    dialogs: {
        dataSource: {
            activeDataSource: undefined | IDataSourceFactory;
            item: undefined | DataSourceDialogItem;
            open: boolean;
        };
        preferences: {
            initialTab: undefined | AppSettingsTab;
            open: boolean;
        };
    };
    featureTours: {
        active: undefined | string;
        shown: string[];
    };
    playbackControls: {
        repeat: boolean;
    };
    sidebars: {
        left: {
            item: undefined | LeftSidebarItemKey;
            open: boolean;
            size: undefined | number;
        };
        right: {
            item: undefined | RightSidebarItemKey;
            open: boolean;
            size: undefined | number;
        };
    };
};
export declare const WorkspaceContext: import("react").Context<StoreApi<WorkspaceContextStore> | undefined>;
export declare const WorkspaceStoreSelectors: {
    selectPanelSettingsOpen: (store: WorkspaceContextStore) => boolean;
};
/**
 * Fetches values from the workspace store.
 */
export declare function useWorkspaceStore<T>(selector: (store: WorkspaceContextStore) => T): T;
