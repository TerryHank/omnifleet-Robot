/// <reference types="react" />
import { SaveConfig } from "@foxglove/studio-base/types/panels";
type Props = {
    config: Record<string, unknown>;
    saveConfig: SaveConfig<Record<string, unknown>>;
    onDownloadImage?: (blob: Blob, fileName: string) => void;
    debugPicking?: boolean;
};
/**
 * The Image panel is a special case of the 3D panel with `interfaceMode` set to `"image"`.
 */
export declare const ImagePanel: import("react").ComponentType<{
    childId?: string | undefined;
    overrideConfig?: Record<string, unknown> | undefined;
    tabId?: string | undefined;
} & Omit<Props, "config" | "saveConfig">> & import("@foxglove/studio-base/components/Panel").PanelStatics<Record<string, unknown>>;
declare const _default: import("react").ComponentType<{
    childId?: string | undefined;
    overrideConfig?: {} | undefined;
    tabId?: string | undefined;
} & Omit<Props, "config" | "saveConfig">> & import("@foxglove/studio-base/components/Panel").PanelStatics<{}>;
export default _default;
