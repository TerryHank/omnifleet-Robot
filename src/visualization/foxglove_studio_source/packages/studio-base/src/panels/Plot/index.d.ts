/// <reference types="react" />
import { PlotConfig } from "./config";
declare const _default: import("react").ComponentType<{
    childId?: string | undefined;
    overrideConfig?: PlotConfig | undefined;
    tabId?: string | undefined;
} & Omit<{
    config: PlotConfig;
    saveConfig: import("../../types/panels").SaveConfig<PlotConfig>;
}, "config" | "saveConfig">> & import("@foxglove/studio-base/components/Panel").PanelStatics<PlotConfig>;
export default _default;
