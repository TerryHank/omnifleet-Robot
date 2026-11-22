import { ScatterDataPoint } from "chart.js";
import { Time } from "@foxglove/studio";
export type Datum = ScatterDataPoint & {
    value: OriginalValue;
    receiveTime: Time;
    headerStamp?: Time;
};
export type OriginalValue = string | bigint | number | boolean | Time;
export declare function isChartValue(value: unknown): value is OriginalValue;
export declare function getChartValue(value: unknown): number | undefined;
