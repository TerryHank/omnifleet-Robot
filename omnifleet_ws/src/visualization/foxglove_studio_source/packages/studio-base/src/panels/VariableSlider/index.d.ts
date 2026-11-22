/// <reference types="react" />
import { SaveConfig } from "@foxglove/studio-base/types/panels";
import { VariableSliderConfig } from "./types";
type Props = {
    config: VariableSliderConfig;
    saveConfig: SaveConfig<VariableSliderConfig>;
};
declare const _default: import("react").ComponentType<{
    childId?: string | undefined;
    overrideConfig?: VariableSliderConfig | undefined;
    tabId?: string | undefined;
} & Omit<Props, "config" | "saveConfig">> & import("@foxglove/studio-base/components/Panel").PanelStatics<VariableSliderConfig>;
export default _default;
