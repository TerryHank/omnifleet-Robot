import { SaveConfig } from "@foxglove/studio-base/types/panels";
import { StateTransitionConfig, StateTransitionPath } from "./types";
export type PathState = {
    path: StateTransitionPath;
    isArray: boolean;
};
export declare function useStateTransitionsPanelSettings(config: StateTransitionConfig, saveConfig: SaveConfig<StateTransitionConfig>, paths: PathState[], focusedPath?: readonly string[]): void;
