/// <reference types="react" />
import { StoryObj } from "@storybook/react";
import { ImageModeConfig } from "@foxglove/studio-base/panels/ThreeDeeRender/IRenderer";
declare const _default: {
    title: string;
    component: import("react").ComponentType<{
        childId?: string | undefined;
        overrideConfig?: Record<string, unknown> | undefined;
        tabId?: string | undefined;
    } & Omit<{
        config: Record<string, unknown>;
        saveConfig: import("../../../../types/panels").SaveConfig<Record<string, unknown>>;
        onDownloadImage?: ((blob: Blob, fileName: string) => void) | undefined;
        debugPicking?: boolean | undefined;
    }, "config" | "saveConfig">> & import("../../../../components/Panel").PanelStatics<Record<string, unknown>>;
    parameters: {
        colorScheme: string;
    };
};
export default _default;
declare const ImageWith3D: (initialConfig: ImageModeConfig) => JSX.Element;
export declare const ImageOnlyModeOff: StoryObj<typeof ImageWith3D>;
export declare const ImageOnlyModeOn: StoryObj<typeof ImageWith3D>;
export declare const ImageOnlyModeOffWithAutoSelectedTopics: StoryObj<typeof ImageWith3D>;
export declare const ImageOnlyModeOffWithAutoSelectedCalibration: StoryObj<typeof ImageWith3D>;
