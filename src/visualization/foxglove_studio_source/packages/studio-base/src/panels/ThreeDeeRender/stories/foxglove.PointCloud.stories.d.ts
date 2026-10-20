/// <reference types="react" />
import { StoryObj } from "@storybook/react";
declare const _default: {
    title: string;
    component: import("react").ComponentType<{
        childId?: string | undefined;
        overrideConfig?: {} | undefined;
        tabId?: string | undefined;
    } & Omit<{
        config: Record<string, unknown>;
        saveConfig: import("../../../types/panels").SaveConfig<Record<string, unknown>>;
        onDownloadImage?: ((blob: Blob, fileName: string) => void) | undefined;
        debugPicking?: boolean | undefined;
    }, "config" | "saveConfig">> & import("../../../components/Panel").PanelStatics<{}>;
    parameters: {
        colorScheme: string;
    };
};
export default _default;
export declare const Foxglove_PointCloud_RGBA_Settings: StoryObj;
export declare const Foxglove_PointCloud_RGBA_SettingsChinese: StoryObj;
export declare const Foxglove_PointCloud_RGBA_SettingsJapanese: StoryObj;
export declare const Foxglove_PointCloud_Gradient_Settings: StoryObj;
export declare const Foxglove_PointCloud_Gradient_SettingsChinese: StoryObj;
export declare const Foxglove_PointCloud_Gradient_SettingsJapanese: StoryObj;
export declare const Foxglove_PointCloud_RGBA: StoryObj;
export declare const Foxglove_PointCloud_RGBA_Square: StoryObj;
export declare const Foxglove_PointCloud_Gradient: StoryObj;
export declare const Foxglove_PointCloud_Gradient_Clamped: StoryObj;
export declare const Foxglove_PointCloud_Stixels: StoryObj;
export declare const Foxglove_PointCloud_Intensity: StoryObj;
export declare const Foxglove_PointCloud_Intensity_Clamped: StoryObj;
export declare const Foxglove_PointCloud_TwoDimensions: StoryObj;
/** Click background to render overall hitmap */
export declare const Foxglove_PointCloud_HistoryPicking: StoryObj;
/** Click first cloud */
export declare const Foxglove_PointCloud_HistoryPickingInstances1: StoryObj;
/** Click second cloud */
export declare const Foxglove_PointCloud_HistoryPickingInstances2: StoryObj;
export declare const Foxglove_PointCloud_Distance: StoryObj;
