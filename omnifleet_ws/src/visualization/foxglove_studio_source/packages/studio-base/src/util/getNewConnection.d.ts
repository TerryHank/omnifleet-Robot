import { Range } from "./ranges";
export declare function getNewConnection(options: {
    currentRemainingRange?: Range;
    readRequestRange?: Range;
    downloadedRanges: Range[];
    lastResolvedCallbackEnd?: number;
    maxRequestSize: number;
    fileSize: number;
    continueDownloadingThreshold: number;
}): Range | undefined;
