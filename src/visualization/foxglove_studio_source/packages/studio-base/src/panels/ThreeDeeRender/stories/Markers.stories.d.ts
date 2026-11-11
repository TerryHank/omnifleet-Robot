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
        chromatic: {
            delay: number;
        };
    };
};
export default _default;
export declare const Markers: StoryObj;
export declare const MarkersSettings: StoryObj;
export declare const MarkersSettingsChinese: StoryObj;
export declare const MarkersSettingsJapanese: StoryObj;
export declare const MarkersNoOutlines: StoryObj;
export declare const EmptyLineStrip: StoryObj;
