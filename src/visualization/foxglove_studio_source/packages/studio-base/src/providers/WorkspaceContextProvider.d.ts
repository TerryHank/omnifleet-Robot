import { ReactNode } from "react";
import { StoreApi } from "zustand";
import { WorkspaceContextStore } from "@foxglove/studio-base/context/Workspace/WorkspaceContext";
/**
 * Creates the default initial state for the workspace store.
 */
export declare function makeWorkspaceContextInitialState(): WorkspaceContextStore;
export default function WorkspaceContextProvider(props: {
    children?: ReactNode;
    disablePersistenceForStorybook?: boolean;
    initialState?: Partial<WorkspaceContextStore>;
    workspaceStoreCreator?: (initialState?: Partial<WorkspaceContextStore>, options?: {
        disablePersistenceForStorybook?: boolean;
    }) => StoreApi<WorkspaceContextStore>;
}): JSX.Element;
