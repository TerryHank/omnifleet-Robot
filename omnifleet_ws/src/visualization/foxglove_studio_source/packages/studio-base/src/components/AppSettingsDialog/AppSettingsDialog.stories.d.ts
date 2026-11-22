/// <reference types="react" />
import { StoryFn, StoryObj } from "@storybook/react";
import { AppSettingsDialog } from "./AppSettingsDialog";
declare function Wrapper(StoryComponent: StoryFn): JSX.Element;
declare const _default: {
    title: string;
    component: typeof AppSettingsDialog;
    parameters: {
        colorScheme: string;
    };
    decorators: (typeof Wrapper)[];
};
export default _default;
export declare const Default: StoryObj;
export declare const DefaultChinese: StoryObj;
export declare const DefaultJapanese: StoryObj;
export declare const ChangingLanguage: StoryObj;
export declare const General: StoryObj;
export declare const GeneralChinese: StoryObj;
export declare const GeneralJapanese: StoryObj;
export declare const Experimental: StoryObj;
export declare const ExperimentalChinese: StoryObj;
export declare const ExperimentalJapanese: StoryObj;
export declare const About: StoryObj;
export declare const AboutChinese: StoryObj;
export declare const AboutJapanese: StoryObj;
