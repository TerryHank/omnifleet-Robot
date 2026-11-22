/// <reference types="react" />
import { Immutable } from "@foxglove/studio";
import { SaveConfig } from "@foxglove/studio-base/types/panels";
import { RawMessagesPanelConfig } from "./types";
type Props = {
    config: Immutable<RawMessagesPanelConfig>;
    saveConfig: SaveConfig<RawMessagesPanelConfig>;
};
declare const _default: import("react").ComponentType<{
    childId?: string | undefined;
    overrideConfig?: RawMessagesPanelConfig | undefined;
    tabId?: string | undefined;
} & Omit<Props, "config" | "saveConfig">> & import("@foxglove/studio-base/components/Panel").PanelStatics<RawMessagesPanelConfig>;
export default _default;
