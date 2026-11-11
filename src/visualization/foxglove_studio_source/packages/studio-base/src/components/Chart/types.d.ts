import { ScatterDataPoint, ChartData as ChartJsChartData } from "chart.js";
declare const ChartNull: null;
type Datum = ScatterDataPoint & {
    label?: string;
    labelColor?: string;
    value?: string | number | bigint | boolean;
    constantName?: string | undefined;
    states?: string[];
};
export type ObjectData = (Datum | typeof ChartNull)[];
export type ChartData = ChartJsChartData<"scatter", ObjectData>;
export type TypedData = {
    x: Float32Array;
    y: Float32Array;
    value: (string | number | bigint | boolean | undefined)[];
    constantName?: string[];
};
export type TypedChartData = ChartJsChartData<"scatter", TypedData[]>;
export type RpcScale = {
    min: number;
    max: number;
    pixelMin: number;
    pixelMax: number;
};
export type RpcScales = {
    x?: RpcScale;
    y?: RpcScale;
};
export type RpcElement = {
    data?: Datum;
    datasetIndex: number;
    index: number;
    view: {
        x: number;
        y: number;
    };
};
export {};
