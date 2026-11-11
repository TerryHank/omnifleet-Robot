import { PropsWithChildren } from "react";
import { ImmutableSettingsTree, PanelStateStore } from "@foxglove/studio-base/context/PanelStateContext";
/**
 * Returns updater function for the current panels settings tree.
 */
export declare function usePanelSettingsTreeUpdate(): (newTree: ImmutableSettingsTree) => void;
/**
 * Returns a [state, setState] pair that can be used to read and update a panel's default title.
 */
export declare function useDefaultPanelTitle(): [
    string | undefined,
    (defaultTitle: string | undefined) => void
];
type Props = PropsWithChildren<{
    initialState?: Partial<PanelStateStore>;
}>;
export declare function PanelStateContextProvider(props: Props): JSX.Element;
export {};
