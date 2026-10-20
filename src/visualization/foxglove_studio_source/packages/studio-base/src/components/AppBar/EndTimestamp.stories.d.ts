import { StoryFn, StoryObj } from "@storybook/react";
import { Time } from "@foxglove/rostime";
import { EndTimestamp } from "./EndTimestamp";
type StoryArgs = {
    time?: Time;
    timezone?: string;
    timeFormat?: "SEC" | "TOD";
};
declare const _default: {
    title: string;
    component: typeof EndTimestamp;
    args: {
        timezone: string;
        time: {
            sec: number;
            nsec: number;
        };
    };
    decorators: ((Story: StoryFn, ctx: import("@storybook/types").StoryContext<import("@storybook/react/dist/types-0fc72a6d").R, {
        time?: Time | undefined;
        timezone?: string | undefined;
        timeFormat?: "SEC" | "TOD" | undefined;
    }>) => JSX.Element)[];
};
export default _default;
type Story = StoryObj<StoryArgs>;
export declare const Default: Story;
export declare const TimeFormatSeconds: Story;
export declare const TimeFormatTOD: StoryObj;
export declare const TimeFormatRelative: StoryObj;
