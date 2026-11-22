import { StoryObj, StoryFn } from "@storybook/react";
import "react-mosaic-component/react-mosaic-component.css";
declare const _default: {
    title: string;
    decorators: ((Story: StoryFn) => JSX.Element)[];
};
export default _default;
type PanelToolbarStoryObj = StoryObj<{
    width?: number;
    layout?: any;
}>;
export declare const NonFloatingNarrow: PanelToolbarStoryObj;
export declare const NonFloatingWideWithPanelName: PanelToolbarStoryObj;
export declare const OneAdditionalIcon: PanelToolbarStoryObj;
export declare const MenuOnlyPanel: PanelToolbarStoryObj;
export declare const MenuLight: PanelToolbarStoryObj;
export declare const MenuWithSiblingPanel: PanelToolbarStoryObj;
export declare const MenuForTabPanel: PanelToolbarStoryObj;
export declare const NoToolbars: PanelToolbarStoryObj;
export declare const Chinese: PanelToolbarStoryObj;
export declare const Japanese: PanelToolbarStoryObj;
