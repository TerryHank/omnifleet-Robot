import { StoryFn, StoryObj } from "@storybook/react";
import StudioToastProvider from "@foxglove/studio-base/components/StudioToastProvider";
declare const _default: {
    title: string;
    component: typeof StudioToastProvider;
    parameters: {
        chromatic: {
            delay: number;
        };
        colorScheme: string;
    };
    decorators: ((Wrapped: StoryFn) => JSX.Element)[];
};
export default _default;
export declare const OneError: StoryObj;
export declare const OneWarning: StoryObj;
export declare const OneInfo: StoryObj;
export declare const MultipleMessages: StoryObj;
export declare const MultipleMessagesLightTheme: StoryObj;
