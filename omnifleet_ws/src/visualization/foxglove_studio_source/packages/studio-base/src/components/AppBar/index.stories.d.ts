import { StoryObj } from "@storybook/react";
import { AppBar } from ".";
import { StorybookDecorator } from "./StorybookDecorator.stories";
declare const _default: {
    title: string;
    component: typeof AppBar;
    decorators: (typeof StorybookDecorator)[];
    args: {
        onMinimizeWindow: import("@storybook/addon-actions").HandlerFunction;
        onMaximizeWindow: import("@storybook/addon-actions").HandlerFunction;
        onUnmaximizeWindow: import("@storybook/addon-actions").HandlerFunction;
        onCloseWindow: import("@storybook/addon-actions").HandlerFunction;
    };
    parameters: {
        colorScheme: string;
    };
};
export default _default;
type Story = StoryObj<typeof AppBar>;
export declare const Default: Story;
export declare const DefaultChinese: Story;
export declare const DefaultJapanese: Story;
export declare const CustomWindowControls: Story;
export declare const CustomWindowControlsMaximized: Story;
export declare const CustomWindowControlsDragRegion: Story;
export declare const PlayerStates: Story;
export declare const PlayerStatesChinese: Story;
export declare const PlayerStatesJapanese: Story;
export declare const DataSources: Story;
export declare const DataSourcesChinese: Story;
export declare const DataSourcesJapanese: Story;
