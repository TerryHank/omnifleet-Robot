/// <reference types="react" />
import { StoryContext, StoryFn, StoryObj } from "@storybook/react";
import { Config } from "./types";
declare const _default: {
    title: string;
    component: import("react").ComponentType<{
        childId?: string | undefined;
        overrideConfig?: {} | undefined;
        tabId?: string | undefined;
    } & Omit<{
        config: Config;
        saveConfig: import("../../types/panels").SaveConfig<Config>;
    }, "config" | "saveConfig">> & import("../../components/Panel").PanelStatics<{}>;
    parameters: {
        colorScheme: string;
    };
    decorators: ((StoryComponent: StoryFn, { parameters }: StoryContext) => JSX.Element)[];
};
export default _default;
export declare const Default: StoryObj;
export declare const DefaultHorizontalLayout: StoryObj;
export declare const CallServiceEnabled: StoryObj;
export declare const CallServiceEnabledServiceName: StoryObj;
export declare const CallServiceEnabledWithCustomButtonSettings: StoryObj;
export declare const WithValidJSON: StoryObj;
export declare const WithInvalidJSON: StoryObj;
export declare const CallingServiceThatDoesNotExist: StoryObj;
