import { StoryObj, StoryFn } from "@storybook/react";
import { CreateEventDialog } from "./CreateEventDialog";
declare const _default: {
    component: typeof CreateEventDialog;
    title: string;
    args: {
        onClose: () => void;
    };
    decorators: ((Wrapped: StoryFn) => JSX.Element)[];
    parameters: {
        colorScheme: string;
    };
};
export default _default;
export declare const Empty: StoryObj;
export declare const Normal: StoryObj;
export declare const WithDuplicates: StoryObj;
