import { Time } from "@foxglove/rostime";
import { MessageAndData } from "@foxglove/studio-base/components/MessagePathSyntax/useCachedGetMessagePathDataItems";
import { ChartDataset } from "@foxglove/studio-base/components/TimeBasedChart/types";
import { StateTransitionPath } from "./types";
type Args = {
    path: StateTransitionPath;
    startTime: Time;
    y: number;
    pathIndex: number;
    blocks: readonly (readonly MessageAndData[] | undefined)[];
    showPoints: boolean;
};
/**
 * Processes messages into datasets. For performance reasons all values are condensed into a single
 * dataset with different labels and colors applied per-point.
 */
export declare function messagesToDataset(args: Args): ChartDataset;
export {};
