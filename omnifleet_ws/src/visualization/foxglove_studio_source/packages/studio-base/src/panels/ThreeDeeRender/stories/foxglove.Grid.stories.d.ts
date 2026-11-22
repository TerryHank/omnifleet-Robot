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
export declare const Foxglove_Grid_Uint8_Values: StoryObj;
export declare const Foxglove_Grid_Uint8_Values_Clamped: StoryObj;
export declare const Foxglove_Grid_RGBA_Values: StoryObj;
export declare const Foxglove_Grid_Float_Values: StoryObj;
export declare const Foxglove_Grid_Float_Values_Clamped: StoryObj;
export declare const Foxglove_Grid_Padded_Row: StoryObj;
