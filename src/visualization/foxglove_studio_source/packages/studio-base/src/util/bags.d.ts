import { Time } from "@foxglove/rostime";
export declare function getBagChunksOverlapCount(chunkInfos: readonly {
    startTime: Time;
    endTime: Time;
}[]): number;
