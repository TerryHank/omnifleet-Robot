import { StoryObj } from "@storybook/react";
import { LayoutData } from "@foxglove/studio-base/context/CurrentLayoutContext";
import Workspace from "./Workspace";
declare const _default: {
    title: string;
    component: typeof Workspace;
    parameters: {
        colorScheme: string;
    };
};
export default _default;
export declare const Basic: StoryObj<{
    initialLayoutState: Partial<LayoutData>;
}>;
export declare const Chinese: typeof Basic;
export declare const Japanese: typeof Basic;
export declare const FullscreenPanel: typeof Basic;
export declare const DragTopicStart: typeof Basic;
export declare const DragTopicOver: typeof Basic;
export declare const DragTopicDrop: typeof Basic;
export declare const DragPathDrop: typeof Basic;
export declare const DragMultipleItems: typeof Basic;
