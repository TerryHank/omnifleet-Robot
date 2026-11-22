/// <reference types="react" />
import { SaveConfig } from "@foxglove/studio-base/types/panels";
import { PublishConfig } from "./types";
type Props = {
    config: PublishConfig;
    saveConfig: SaveConfig<PublishConfig>;
};
declare const _default: import("react").ComponentType<{
    childId?: string | undefined;
    overrideConfig?: PublishConfig | undefined;
    tabId?: string | undefined;
} & Omit<Props, "config" | "saveConfig">> & import("@foxglove/studio-base/components/Panel").PanelStatics<PublishConfig>;
export default _default;
