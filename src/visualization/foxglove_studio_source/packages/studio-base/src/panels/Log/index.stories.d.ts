/// <reference types="react" />
import { StoryObj } from "@storybook/react";
declare const _default: {
    title: string;
    component: import("react").ComponentType<{
        childId?: string | undefined;
        overrideConfig?: import("./types").Config | undefined;
        tabId?: string | undefined;
    } & Omit<{
        config: import("./types").Config;
        saveConfig: import("../../types/panels").SaveConfig<import("./types").Config>;
    }, "config" | "saveConfig">> & import("../../components/Panel").PanelStatics<import("./types").Config>;
};
export default _default;
export declare const Simple: StoryObj;
export declare const Scrolled: StoryObj;
export declare const WithSettings: StoryObj;
export declare const TopicToRenderWithSettings: StoryObj;
export declare const FilteredTerms: StoryObj;
export declare const CaseInsensitiveFilter: StoryObj;
export declare const FoxgloveLog: StoryObj;
export declare const FilterByName: StoryObj;
