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
export declare const EmptyState: StoryObj;
export declare const SinglePoint: StoryObj;
export declare const SinglePointWithMissingValues: StoryObj;
export declare const SinglePointWithInvalidData: StoryObj;
export declare const SinglePointWithNoFix: StoryObj;
export declare const SinglePointWithSettings: StoryObj;
export declare const SinglePointWithSettingsOverride: StoryObj;
export declare const MultipleTopics: StoryObj;
export declare const SinglePointDiagonalCovariance: StoryObj;
export declare const SinglePointFullCovariance: StoryObj;
export declare const GeoJSON: StoryObj;
