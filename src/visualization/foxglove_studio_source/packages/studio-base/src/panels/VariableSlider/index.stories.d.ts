/// <reference types="react" />
import { StoryObj } from "@storybook/react";
declare const _default: {
    title: string;
    component: import("react").ComponentType<{
        childId?: string | undefined;
        overrideConfig?: import("./types").VariableSliderConfig | undefined;
        tabId?: string | undefined;
    } & Omit<{
        config: import("./types").VariableSliderConfig;
        saveConfig: import("../../types/panels").SaveConfig<import("./types").VariableSliderConfig>;
    }, "config" | "saveConfig">> & import("../../components/Panel").PanelStatics<import("./types").VariableSliderConfig>;
};
export default _default;
export declare const Example: StoryObj;
export declare const NarrowLayout: StoryObj;
export declare const WithSettings: StoryObj;
