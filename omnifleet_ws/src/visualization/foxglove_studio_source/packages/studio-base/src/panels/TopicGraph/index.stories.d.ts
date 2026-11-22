/// <reference types="react" />
import { StoryObj } from "@storybook/react";
declare const _default: {
    title: string;
    component: import("react").ComponentType<{
        childId?: string | undefined;
        overrideConfig?: {} | undefined;
        tabId?: string | undefined;
    } & Omit<{
        config: {};
        saveConfig: import("../../types/panels").SaveConfig<{}>;
    }, "config" | "saveConfig">> & import("../../components/Panel").PanelStatics<{}>;
};
export default _default;
export declare const Empty: StoryObj;
export declare const WithSettings: StoryObj;
export declare const AllTopics: StoryObj;
export declare const TopicsWithSubscribers: StoryObj;
export declare const TopicsHidden: StoryObj;
export declare const ReLayout: StoryObj;
