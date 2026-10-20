import { PopoverPosition, PopoverReference } from "@mui/material";
import { StoryObj } from "@storybook/react";
import { AppMenu } from "./AppMenu";
type StoryArgs = {
    handleClose: () => void;
    anchorEl?: HTMLElement;
    anchorReference?: PopoverReference;
    anchorPosition?: PopoverPosition;
    disablePortal?: boolean;
    open: boolean;
    testId?: string;
};
declare const _default: {
    title: string;
    component: typeof AppMenu;
    args: {
        open: true;
        anchorPosition: {
            top: number;
            left: number;
        };
        anchorReference: "anchorPosition";
        disablePortal: true;
        handleClose: (...args: any[]) => void;
    };
    decorators: ((Story: import("@storybook/types").PartialStoryFn<import("@storybook/react/dist/types-0fc72a6d").R, {
        handleClose: () => void;
        anchorEl?: HTMLElement | undefined;
        anchorReference?: PopoverReference | undefined;
        anchorPosition?: PopoverPosition | undefined;
        disablePortal?: boolean | undefined;
        open: boolean;
        testId?: string | undefined;
    }>, { args: { testId: _testId, ...args } }: import("@storybook/types").StoryContext<import("@storybook/react/dist/types-0fc72a6d").R, {
        handleClose: () => void;
        anchorEl?: HTMLElement | undefined;
        anchorReference?: PopoverReference | undefined;
        anchorPosition?: PopoverPosition | undefined;
        disablePortal?: boolean | undefined;
        open: boolean;
        testId?: string | undefined;
    }>) => JSX.Element)[];
    play: ({ canvasElement, args }: import("@storybook/types").PlayFunctionContext<import("@storybook/react/dist/types-0fc72a6d").R, StoryArgs>) => Promise<void>;
};
export default _default;
type Story = StoryObj<StoryArgs>;
export declare const Default: Story;
export declare const FileMenuDark: Story;
export declare const FileMenuDarkChinese: Story;
export declare const FileMenuDarkJapanese: Story;
export declare const FileMenuLight: Story;
export declare const FileMenuLightChinese: Story;
export declare const FileMenuLightJapanese: Story;
export declare const ViewMenuDark: Story;
export declare const ViewMenuDarkChinese: Story;
export declare const ViewMenuDarkJapanese: Story;
export declare const ViewMenuLight: Story;
export declare const ViewMenuLightChinese: Story;
export declare const ViewMenuLightJapanese: Story;
export declare const HelpMenuDark: Story;
export declare const HelpMenuDarkChinese: Story;
export declare const HelpMenuDarkJapanese: Story;
export declare const HelpMenuLight: Story;
export declare const HelpMenuLightChinese: Story;
export declare const HelpMenuLightJapanese: Story;
