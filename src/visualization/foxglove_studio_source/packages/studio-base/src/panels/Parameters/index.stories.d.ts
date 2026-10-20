/// <reference types="react" />
import { StoryObj } from "@storybook/react";
declare const _default: {
    title: string;
    component: import("react").ComponentType<{
        childId?: string | undefined;
        overrideConfig?: {
            title: string;
        } | undefined;
        tabId?: string | undefined;
    } & Omit<{
        config: {
            title: string;
        };
        saveConfig: import("../../types/panels").SaveConfig<{
            title: string;
        }>;
    }, "config" | "saveConfig">> & import("../../components/Panel").PanelStatics<{
        title: string;
    }>;
};
export default _default;
export declare const Default: StoryObj;
export declare const WithParameters: StoryObj;
export declare const WithEditableParameters: StoryObj;
