import { RpcScales } from "@foxglove/studio-base/components/Chart/types";
import { ChartDatasets, PlotViewport } from "./types";
type UpdateParams = {
    datasets?: ChartDatasets;
    datasetBounds?: PlotViewport;
    scales?: RpcScales;
};
/**
 * Track a dataset, some bounds, a viewport to perform downsampling
 */
export declare class Downsampler {
    #private;
    /**
     * Update internal state for next downsample
     */
    update(opt: UpdateParams): void;
    /**
     * Perform a downsample with the latest state
     */
    downsample(): ChartDatasets | undefined;
}
export {};
