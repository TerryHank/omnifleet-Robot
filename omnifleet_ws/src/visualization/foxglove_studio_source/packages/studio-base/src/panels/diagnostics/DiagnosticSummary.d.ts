/// <reference types="react" />
import { SaveConfig } from "@foxglove/studio-base/types/panels";
import { DiagnosticSummaryConfig } from "./util";
type Props = {
    config: DiagnosticSummaryConfig;
    saveConfig: SaveConfig<DiagnosticSummaryConfig>;
};
declare const _default: import("react").ComponentType<{
    childId?: string | undefined;
    overrideConfig?: DiagnosticSummaryConfig | undefined;
    tabId?: string | undefined;
} & Omit<Props, "config" | "saveConfig">> & import("@foxglove/studio-base/components/Panel").PanelStatics<DiagnosticSummaryConfig>;
export default _default;
