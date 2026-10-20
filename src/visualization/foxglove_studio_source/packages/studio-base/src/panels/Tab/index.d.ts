/// <reference types="react" />
import { TabPanelConfig as Config } from "@foxglove/studio-base/types/layouts";
import { SaveConfig } from "@foxglove/studio-base/types/panels";
type Props = {
    config: Config;
    saveConfig: SaveConfig<Config>;
};
declare const _default: import("react").ComponentType<{
    childId?: string | undefined;
    overrideConfig?: Config | undefined;
    tabId?: string | undefined;
} & Omit<Props, "config" | "saveConfig">> & import("@foxglove/studio-base/components/Panel").PanelStatics<Config>;
export default _default;
