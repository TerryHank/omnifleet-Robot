/// <reference types="react" />
import { SaveConfig } from "@foxglove/studio-base/types/panels";
type Props = {
    config: {
        type: string;
        id: string;
    };
    saveConfig: SaveConfig<unknown>;
};
/**
 * An UnknownPanel stands in for missing panels. When a panel referenced in a layout is not
 * available (maybe the extension was un-installed), this panel is shown instead.
 */
export declare const UnknownPanel: import("react").ComponentType<{
    childId?: string | undefined;
    overrideConfig?: {} | undefined;
    tabId?: string | undefined;
} & Omit<Props, "config" | "saveConfig">> & import("@foxglove/studio-base/components/Panel").PanelStatics<{}>;
export {};
