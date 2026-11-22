import { Time } from "@foxglove/rostime";
import PlayerProblemManager from "@foxglove/studio-base/players/PlayerProblemManager";
import { Progress, TopicSelection } from "@foxglove/studio-base/players/types";
import { IIterableSource } from "./IIterableSource";
export declare const MEMORY_INFO_PRELOADED_MSGS = "Preloaded messages";
type BlockLoaderArgs = {
    cacheSizeBytes: number;
    source: IIterableSource;
    start: Time;
    end: Time;
    maxBlocks: number;
    minBlockDurationNs: number;
    problemManager: PlayerProblemManager;
};
type LoadArgs = {
    progress: (progress: Progress) => void;
};
/**
 * BlockLoader manages loading blocks from a source. Blocks are fixed time span containers for messages.
 */
export declare class BlockLoader {
    #private;
    constructor(args: BlockLoaderArgs);
    setTopics(topics: TopicSelection): void;
    stopLoading(): Promise<void>;
    startLoading(args: LoadArgs): Promise<void>;
}
export {};
