import { ChartOptions, InteractionMode, ScaleOptions } from "chart.js";
import { AnnotationOptions } from "chartjs-plugin-annotation";
import { ComponentProps } from "react";
import ChartComponent from "@foxglove/studio-base/components/Chart/index";
import { Bounds } from "@foxglove/studio-base/types/Bounds";
import { TimeBasedChartTooltipData } from "./TimeBasedChartTooltipContent";
import { ObjectDataProvider, TypedDataProvider } from "./types";
type ChartComponentProps = ComponentProps<typeof ChartComponent>;
type ChartDefaultView = {
    type: "fixed";
    minXValue: number;
    maxXValue: number;
} | {
    type: "following";
    width: number;
};
export type Props = {
    type: "scatter";
    width: number;
    height: number;
    zoom: boolean;
    data?: ChartComponentProps["data"];
    provider?: ObjectDataProvider;
    typedData?: ChartComponentProps["typedData"];
    typedProvider?: TypedDataProvider;
    dataBounds?: Bounds;
    tooltips?: Map<string, TimeBasedChartTooltipData>;
    xAxes?: ScaleOptions<"linear">;
    yAxes: ScaleOptions<"linear">;
    annotations?: AnnotationOptions[];
    resetButtonPaddingBottom?: number;
    isSynced?: boolean;
    linesToHide?: {
        [key: string]: boolean;
    };
    interactionMode?: InteractionMode;
    datasetId?: string;
    onClick?: ChartComponentProps["onClick"];
    xAxisIsPlaybackTime: boolean;
    showXAxisLabels: boolean;
    plugins?: ChartOptions["plugins"];
    currentTime?: number;
    defaultView?: ChartDefaultView;
};
export default function TimeBasedChart(props: Props): JSX.Element;
export {};
