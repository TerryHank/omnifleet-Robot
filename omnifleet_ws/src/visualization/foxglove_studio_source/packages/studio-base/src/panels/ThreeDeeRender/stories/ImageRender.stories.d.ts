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
export declare const ImageRender: StoryObj<{
    includeSettings: boolean;
}>;
export declare const ImageRenderSettings: typeof ImageRender;
export declare const ImageRenderSettingsChinese: typeof ImageRender;
export declare const ImageRenderSettingsJapanese: typeof ImageRender;
export declare const FoxgloveImage: StoryObj;
export declare const ImageThenInfo: StoryObj;
export declare const InfoThenImage: StoryObj;
export declare const UpdateImageToGreen: StoryObj;
