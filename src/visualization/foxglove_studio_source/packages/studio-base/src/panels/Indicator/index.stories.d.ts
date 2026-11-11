/// <reference types="react" />
import { StoryFn, StoryContext, StoryObj } from "@storybook/react";
declare const _default: {
    title: string;
    component: import("react").ComponentType<{
        childId?: string | undefined;
        overrideConfig?: {} | undefined;
        tabId?: string | undefined;
    } & Omit<{
        config: import("./types").Config;
        saveConfig: import("../../types/panels").SaveConfig<import("./types").Config>;
    }, "config" | "saveConfig">> & import("../../components/Panel").PanelStatics<{}>;
    decorators: ((StoryComponent: StoryFn, { parameters }: StoryContext) => JSX.Element)[];
};
export default _default;
export declare const EmptyState: StoryObj;
export declare const MissingValue: StoryObj;
export declare const BackgroundStyle: StoryObj;
export declare const BooleanTrue: StoryObj;
export declare const BooleanFalse: StoryObj;
export declare const String: StoryObj;
export declare const NumberNegative: StoryObj;
export declare const NumberZero: StoryObj;
export declare const NumberPositive: StoryObj;
export declare const MessagePathWithFilter: StoryObj;
