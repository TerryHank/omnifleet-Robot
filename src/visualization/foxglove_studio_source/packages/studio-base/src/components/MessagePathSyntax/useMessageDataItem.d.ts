import { MessageEvent } from "@foxglove/studio-base/players/types";
import { MessageAndData } from "./useCachedGetMessagePathDataItems";
type Options = {
    historySize: number;
};
type ReducedValue = {
    matches: MessageAndData[];
    messageEvents: readonly Readonly<MessageEvent>[];
    path: string;
};
/**
 * Return an array of MessageAndData[] for matching messages on @param path.
 *
 * The first array item is the oldest matched message, and the last item is the newest.
 *
 * The `historySize` option configures how many matching messages to keep. The default is 1.
 */
export declare function useMessageDataItem(path: string, options?: Options): ReducedValue["matches"];
export {};
