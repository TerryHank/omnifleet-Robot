import { StoryObj } from "@storybook/react";
import TimeBasedChart from "./index";
declare const _default: {
    title: string;
    component: typeof TimeBasedChart;
    parameters: {
        chromatic: {
            delay: number;
        };
        colorScheme: string;
        disableI18n: boolean;
    };
};
export default _default;
export declare const Simple: StoryObj;
export declare const SimpleLight: StoryObj;
export declare const CanZoomAndUpdate: StoryObj;
export declare const CleansUpTooltipOnUnmount: StoryObj;
export declare const CallPauseOnInitialMount: StoryObj;
export declare const ResumeFrameOnUnmount: StoryObj;
