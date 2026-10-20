/// <reference types="react" />
import { StoryObj, StoryFn } from "@storybook/react";
import { EventsList } from "./EventsList";
declare function Wrapper(Child: StoryFn): JSX.Element;
declare const _default: {
    title: string;
    component: typeof EventsList;
    decorators: (typeof Wrapper)[];
};
export default _default;
export declare const Default: StoryObj;
export declare const Selected: StoryObj;
export declare const WithError: StoryObj;
export declare const Loading: StoryObj;
