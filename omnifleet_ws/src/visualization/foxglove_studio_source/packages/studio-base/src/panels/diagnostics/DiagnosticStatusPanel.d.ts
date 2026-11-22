/// <reference types="react" />
import { SaveConfig } from "@foxglove/studio-base/types/panels";
import { DiagnosticStatusConfig as Config } from "./util";
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
