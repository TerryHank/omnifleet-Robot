/// <reference types="react" />
import { StoryObj, StoryFn } from "@storybook/react";
import { PlaybackControlsTooltipContent } from "@foxglove/studio-base/components/PlaybackControls/PlaybackControlsTooltipContent";
declare function Wrapper(Wrapped: StoryFn): JSX.Element;
declare const _default: {
    component: typeof PlaybackControlsTooltipContent;
    title: string;
    decorators: (typeof Wrapper)[];
};
export default _default;
export declare const Default: StoryObj;
export declare const WithEvents: StoryObj;
