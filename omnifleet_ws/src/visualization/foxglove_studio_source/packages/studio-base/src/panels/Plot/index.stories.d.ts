/// <reference types="react" />
import { StoryObj } from "@storybook/react";
import { Fixture } from "@foxglove/studio-base/stories/PanelSetup";
import { PlotConfig } from "./config";
declare function PlotWrapper(props: {
    style?: {
        [key: string]: string | number;
    };
    includeSettings?: boolean;
    fixture?: Fixture;
    config: PlotConfig;
}): JSX.Element;
declare const _default: {
    title: string;
    component: typeof PlotWrapper;
    parameters: {
        colorScheme: string;
        chromatic: {
            delay: number;
        };
    };
};
export default _default;
export declare const Empty: StoryObj<typeof PlotWrapper>;
export declare const LineGraph: StoryObj<typeof PlotWrapper>;
export declare const LineGraphWithValuesAndDisabledSeries: StoryObj<typeof PlotWrapper>;
export declare const LineGraphWithXMinMax: StoryObj;
export declare const LineGraphWithXRange: StoryObj;
export declare const LineGraphWithSettings: StoryObj;
export declare const LineGraphWithSettingsChinese: StoryObj;
export declare const LineGraphWithSettingsJapanese: StoryObj;
export declare const LineGraphWithLegendsHidden: StoryObj;
export declare const InALineGraphWithMultiplePlotsXAxesAreSynced: StoryObj;
export declare const LineGraphAfterZoom: StoryObj;
export declare const TimestampMethodHeaderStamp: StoryObj;
export declare const LongPath: StoryObj;
export declare const HiddenConnectingLines: StoryObj;
export declare const ReferenceLine: StoryObj;
export declare const WithMinAndMaxYValues: StoryObj;
export declare const WithJustMinYValueLessThanMinimumValue: StoryObj;
export declare const WithJustMinYValueMoreThanMinimumValue: StoryObj;
export declare const WithJustMinYValueMoreThanMaximumValue: StoryObj;
export declare const WithJustMaxYValueLessThanMaximumValue: StoryObj;
export declare const WithJustMaxYValueMoreThanMaximumValue: StoryObj;
export declare const WithJustMaxYValueLessThanMinimumValue: StoryObj;
export declare const IndexBasedXAxisForArray: StoryObj;
export declare const IndexBasedXAxisForArrayWithUpdate: StoryObj;
export declare const CustomXAxisTopic: StoryObj;
export declare const CustomXAxisTopicWithXLimits: StoryObj;
export declare const CurrentCustomXAxisTopic: StoryObj;
export declare const CustomXAxisTopicWithMismatchedDataLengths: StoryObj;
export declare const SuperCloseValues: StoryObj;
export declare const TimeValues: StoryObj;
export declare const PreloadedDataInBinaryBlocks: StoryObj;
export declare const MixedStreamedAndPreloadedData: StoryObj;
export declare const PreloadedDataAndItsDerivative: StoryObj;
export declare const PreloadedDataAndItsNegative: StoryObj;
export declare const PreloadedDataAndItsAbsoluteValue: StoryObj;
export declare const LegendLeft: StoryObj;
export declare const LegendTop: StoryObj;
