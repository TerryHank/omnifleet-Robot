import { Point } from "@foxglove/studio-base/components/Chart/datasets";
import type { PlotViewport } from "./types";
export declare const MAX_POINTS = 5000;
export declare const MINIMUM_PIXEL_DISTANCE = 3;
type IntervalItem = {
    xPixel: number;
    yPixel: number;
    label: string | undefined;
    index: number;
};
export type DownsampleState = {
    cursor: number;
    pixelPerXValue: number;
    pixelPerYValue: number;
    intFirst: IntervalItem | undefined;
    intLast: IntervalItem | undefined;
    intMin: IntervalItem | undefined;
    intMax: IntervalItem | undefined;
};
/**
 * Calculate the size of the intervals the downsampling operation should use,
 * expressed as a ratio of pixels to units in the coordinate frame of the plot.
 */
export declare function calculateIntervals(view: PlotViewport, pointsPerInterval: number, maxPoints?: number): {
    pixelPerXValue: number;
    pixelPerYValue: number;
};
/**
 * Initialize a stateful downsampling operation with a fixed viewport and
 * maximum number of points.
 */
export declare function initDownsample(view: PlotViewport, maxPoints?: number): DownsampleState;
/**
 * Complete a downsampling operation by calculating the indices the last
 * interval produced.
 */
export declare function finishDownsample(state: DownsampleState): number[];
/**
 * Consume the provided `points` and return both the indices consuming these
 * points produced and the new state of the downsampling operation.
 *
 * `points` should consist solely of _new_ points.
 */
export declare function continueDownsample(points: Iterable<Point>, state: DownsampleState): [number[], DownsampleState];
/**
 * Downsample a timeseries dataset by returning the indices of a subset of
 * points that are deemed to be representative of the original dataset when
 * rendered with the given viewport.
 *
 * This function assumes that points are sorted and that x- values are
 * monotonically increasing.
 *
 * If `maxPoints` is provided, downsampleTimeseries will return only up to `maxPoints` points.
 *
 * The downsampled data preserves the shape of the original data. The algorithm does this by
 * downsampling within an interval. Each interval tracks the first datum of the interval,
 * minimum y-value datum, maximum y-value datum, and the last datum of the interval.
 *
 * For each datum within the dataset, we determine first if it falls within the current interval.
 * - If the datum falls within the current interval we update the min/max y or last values. Then move
 *   to the next datum.
 * - If the datum falls outside the current interval, we determine whether to add the min/max and
 *   last datum to the downsampled dataset, and then move to the next datum.
 * - If first/min/max/last are all the same datum, then only one datum appears in the downsampled
 *   dataset.
 *
 * By tracking the first/min/max/last within an interval, the shape of the original data is preserved.
 * Points before the interval connect into the interval with the same slope line as the original
 * dataset, and the interval connects to the next interval with the same slope line as the original
 * data. The min/max entries preserve spikes within the data.
 */
export declare function downsampleTimeseries(points: Iterable<Point>, view: PlotViewport, maxPoints?: number): number[];
export declare function downsampleScatter(points: Iterable<Point>, view: PlotViewport): number[];
export {};
