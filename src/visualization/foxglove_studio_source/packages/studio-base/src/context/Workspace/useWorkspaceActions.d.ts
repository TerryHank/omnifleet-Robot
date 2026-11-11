import { Dispatch, SetStateAction } from "react";
import { AppSettingsTab } from "@foxglove/studio-base/components/AppSettingsDialog/AppSettingsDialog";
import { DataSourceDialogItem } from "@foxglove/studio-base/components/DataSourceDialog";
import { IDataSourceFactory } from "@foxglove/studio-base/context/PlayerSelectionContext";
import { LeftSidebarItemKey, RightSidebarItemKey } from "./WorkspaceContext";
export type WorkspaceActions = {
    dialogActions: {
        dataSource: {
            close: () => void;
            open: (item: DataSourceDialogItem, dataSource?: IDataSourceFactory) => void;
        };
        openFile: {
            open: () => Promise<void>;
        };
        preferences: {
            close: () => void;
            open: (initialTab?: AppSettingsTab) => void;
        };
    };
    featureTourActions: {
        startTour: (tour: string) => void;
        finishTour: (tour: string) => void;
    };
    openPanelSettings: () => void;
    playbackControlActions: {
        setRepeat: Dispatch<SetStateAction<boolean>>;
    };
    sidebarActions: {
        left: {
            selectItem: (item: undefined | LeftSidebarItemKey) => void;
            setOpen: Dispatch<SetStateAction<boolean>>;
            setSize: (size: undefined | number) => void;
        };
        right: {
            selectItem: (item: undefined | RightSidebarItemKey) => void;
            setOpen: Dispatch<SetStateAction<boolean>>;
            setSize: (size: undefined | number) => void;
        };
    };
    layoutActions: {
        importFromFile: () => void;
        exportToFile: () => void;
    };
};
/**
 * Provides various actions to manipulate the workspace state.
 */
export declare function useWorkspaceActions(): WorkspaceActions;
