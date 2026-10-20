/// <reference types="react" />
import { StoryObj } from "@storybook/react";
declare const _default: {
    title: string;
    component: import("react").ComponentType<{
        childId?: string | undefined;
        overrideConfig?: import("./types").StateTransitionConfig | undefined;
        tabId?: string | undefined;
    } & Omit<{
        config: import("./types").StateTransitionConfig;
        saveConfig: import("../../types/panels").SaveConfig<import("./types").StateTransitionConfig>;
    }, "config" | "saveConfig">> & import("../../components/Panel").PanelStatics<import("./types").StateTransitionConfig>;
    parameters: {
        colorScheme: string;
        chromatic: {
            delay: number;
        };
    };
};
export default _default;
export declare const Empty: StoryObj;
export declare const ColorPalette: StoryObj;
export declare const CloseValues: StoryObj;
export declare const OnePath: StoryObj;
export declare const WithXAxisMinMax: StoryObj;
export declare const WithXAxisRange: StoryObj;
export declare const WithSettings: StoryObj;
export declare const MultiplePaths: StoryObj;
export declare const LongPath: StoryObj;
export declare const ColorClash: StoryObj;
export declare const Blocks: StoryObj;
