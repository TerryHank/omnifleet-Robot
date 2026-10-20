/// <reference types="react" />
import { StoryObj } from "@storybook/react";
import { PublishClickType } from "../renderables/PublishClickTool";
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
export declare const Point: StoryObj<{
    type: PublishClickType;
}>;
export declare const PosePosition: StoryObj<{
    type: PublishClickType;
}>;
export declare const PoseComplete: StoryObj<{
    type: PublishClickType;
}>;
export declare const PoseEstimatePosition: StoryObj<{
    type: PublishClickType;
}>;
export declare const PoseEstimateComplete: StoryObj<{
    type: PublishClickType;
}>;
export declare const Settings: StoryObj<typeof PublishClickToolTemplate>;
export declare const SettingsChinese: StoryObj<typeof PublishClickToolTemplate>;
export declare const SettingsJapanese: StoryObj<typeof PublishClickToolTemplate>;
declare function PublishClickToolTemplate({ type, includeSettings, }: {
    type: PublishClickType;
    includeSettings?: boolean;
}): JSX.Element;
