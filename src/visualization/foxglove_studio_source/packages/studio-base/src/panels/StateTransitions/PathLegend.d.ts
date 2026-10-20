/// <reference types="react" />
import { StateTransitionConfig, StateTransitionPath } from "@foxglove/studio-base/panels/StateTransitions/types";
import { SaveConfig } from "@foxglove/studio-base/types/panels";
export declare const PathLegend: import("react").NamedExoticComponent<{
    paths: StateTransitionPath[];
    heightPerTopic: number;
    setFocusedPath: (value: string[] | undefined) => void;
    saveConfig: SaveConfig<StateTransitionConfig>;
}>;
