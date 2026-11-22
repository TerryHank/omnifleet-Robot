/// <reference types="react" />
import { StoryObj } from "@storybook/react";
import { PanelOverlay } from "./PanelOverlay";
declare const _default: import("@storybook/types").ComponentAnnotations<import("@storybook/react/dist/types-0fc72a6d").R, import("./PanelOverlay").PanelOverlayProps & import("react").RefAttributes<HTMLDivElement>>;
export default _default;
type Story = StoryObj<typeof PanelOverlay>;
export declare const Default: Story;
export declare const ValidDropTarget: Story;
export declare const InvalidDropTarget: Story;
export declare const SelectedPanelActions: Story;
export declare const QuickActions: Story;
