/// <reference types="react" />
import { StoryFn, StoryContext, StoryObj } from "@storybook/react";
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
    decorators: ((StoryComponent: StoryFn, context: StoryContext) => JSX.Element)[];
};
export default _default;
export declare const Unconfigured: StoryObj;
export declare const WithSettings: StoryObj;
export declare const WithTopic: StoryObj;
