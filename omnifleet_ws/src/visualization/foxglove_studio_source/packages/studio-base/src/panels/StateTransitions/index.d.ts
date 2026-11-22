/// <reference types="react" />
import { SaveConfig } from "@foxglove/studio-base/types/panels";
import { StateTransitionConfig } from "./types";
type Props = {
    config: StateTransitionConfig;
    saveConfig: SaveConfig<StateTransitionConfig>;
};
declare const _default: import("react").ComponentType<{
    childId?: string | undefined;
    overrideConfig?: StateTransitionConfig | undefined;
    tabId?: string | undefined;
} & Omit<Props, "config" | "saveConfig">> & import("@foxglove/studio-base/components/Panel").PanelStatics<StateTransitionConfig>;
export default _default;
