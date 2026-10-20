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
export declare const Occupancy_Grid_Costmap: StoryObj;
export declare const Occupancy_Grid_Costmap_With_Pick_Settings: StoryObj;
export declare const OccupancyGridCostmapWithSettingsChinese: StoryObj;
export declare const OccupancyGridCostmapWithSettingsJapanese: StoryObj;
