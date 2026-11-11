import { ChartData, ChartOptions } from "chart.js";
import Rpc from "@foxglove/studio-base/util/Rpc";
import { TypedChartData } from "../types";
export type ChartUpdateMessage = {
    data?: ChartData<"scatter">;
    typedData?: TypedChartData;
    height?: number;
    options?: ChartOptions;
    isBoundsReset: boolean;
    width?: number;
};
export default class ChartJsMux {
    #private;
    constructor(rpc: Rpc);
}
