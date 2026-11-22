/// <reference types="react" />
import { SaveConfig } from "@foxglove/studio-base/types/panels";
declare const _default: import("react").ComponentType<{
    childId?: string | undefined;
    overrideConfig?: {} | undefined;
    tabId?: string | undefined;
} & Omit<{
    config: {};
    saveConfig: SaveConfig<{}>;
}, "config" | "saveConfig">> & import("@foxglove/studio-base/components/Panel").PanelStatics<{}>;
export default _default;
