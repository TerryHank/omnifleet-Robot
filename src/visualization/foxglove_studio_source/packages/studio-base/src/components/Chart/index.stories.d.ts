import { StoryObj } from "@storybook/react";
import ChartComponent from ".";
declare const _default: {
    title: string;
    component: typeof ChartComponent;
    parameters: {
        chromatic: {
            delay: number;
        };
        colorScheme: string;
        disableI18n: boolean;
    };
};
export default _default;
export declare const Basic: StoryObj;
export declare const WithDatalabels: StoryObj;
export declare const AllowsClickingOnDatalabels: StoryObj;
