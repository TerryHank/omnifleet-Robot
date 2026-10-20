import type { ChartData as AbstractChartData } from "chart.js";
import type { ObjectData, ChartData, TypedChartData, TypedData } from "@foxglove/studio-base/components/Chart/types";
export type ChartDatasets = ChartData["datasets"];
export type ChartDataset = ChartDatasets[0];
export type ChartDatum = ChartDataset["data"][0];
export type TypedChartDatasets = TypedChartData["datasets"];
export type TypedChartDataset = TypedChartDatasets[0];
export type Bounds1D = {
    min: number;
    max: number;
};
export type Bounds = {
    x: Bounds1D;
    y: Bounds1D;
};
/**
 * PlotViewport represents the visible region of a plot in terms of its axes
 * and its dimensions on the screen.
 */
export type PlotViewport = {
    width: number;
    height: number;
    bounds: Bounds;
};
export type ProviderState<T> = {
    data: AbstractChartData<"scatter", T>;
    bounds: Bounds;
};
export type ChartProviderState = ProviderState<ObjectData>;
export type TypedProviderState = ProviderState<TypedData[]>;
export type ProviderStateSetter<T> = (state: ProviderState<T>) => void;
/**
 * PlotDataProvider gives the user of a TimeBasedChart more granular control
 * over the data the plot displays, including giving it access to the current
 * viewport.
 */
export type PlotDataProvider<T> = {
    setView: (view: PlotViewport) => void;
    register: (setter: ProviderStateSetter<T>, addPartial: ProviderStateSetter<T>) => void;
};
export type ObjectDataProvider = PlotDataProvider<ObjectData>;
export type TypedDataProvider = PlotDataProvider<TypedData[]>;
