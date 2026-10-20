import { Point } from "@foxglove/studio-base/components/Chart/datasets";
import type { PlotViewport } from "./types";
export type StatePoint = {
    x: number;
    index: number | undefined;
    states?: string[];
};
/**
 * Downsample state transition data by breaking the visible bounds into a set
 * of evenly-sized intervals and making a note of the number of state
 * transitions (between distinct states) that occur in each.
 *
 * If just one occurs, we return a StatePoint with x == the x-coordinate of the
 * single state transition point and index == the index of that point.
 *
 * If more than one does, it's represented in the output as two StatePoints:
 * one that matches the first point found in the interval (except with index ==
 * undefined) and another that matches the _last_ point in the interval, with x
 * == the end of the interval in the coordinate frame of the plot.
 *
 * This allows the caller to render intervals that contain more state
 * transitions than we can safely render in a different way to make it obvious
 * to the user that there is more detail.
 *
 * The `maxPoints` parameter works identically to the way it does in
 * `downsampleTimeseries`.
 */
export declare function downsampleStates(points: Iterable<Point>, view: PlotViewport, maxPoints?: number): StatePoint[];
