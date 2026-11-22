import EventEmitter from "eventemitter3";
import { MessageEvent, Time } from "@foxglove/studio";
import { Range } from "@foxglove/studio-base/util/ranges";
import { GetBackfillMessagesArgs, IIterableSource, Initalization, IteratorResult, MessageIteratorArgs } from "./IIterableSource";
type Options = {
    maxBlockSize?: number;
    maxTotalSize?: number;
};
interface EventTypes {
    /** Dispatched when the loaded ranges have changed. Use `loadedRanges()` to get the new ranges. */
    loadedRangesChange: () => void;
}
/**
 * CachingIterableSource proxies access to IIterableSource through a memory buffer.
 *
 * Message reading occurs from the memory buffer containing previously read messages. If there is no
 * buffer for previously read messages, then the underlying source is used and the messages are
 * cached when read.
 */
declare class CachingIterableSource extends EventEmitter<EventTypes> implements IIterableSource {
    #private;
    constructor(source: IIterableSource, opt?: Options);
    initialize(): Promise<Initalization>;
    terminate(): Promise<void>;
    loadedRanges(): Range[];
    getCacheSize(): number;
    messageIterator(args: MessageIteratorArgs): AsyncIterableIterator<Readonly<IteratorResult>>;
    getBackfillMessages(args: GetBackfillMessagesArgs): Promise<MessageEvent[]>;
    /**
     * Update the current read head, such that the source can determine which blocks are evictable.
     * @param readHead current read head
     */
    setCurrentReadHead(readHead: Time): void;
    /**
     * Checks if the current cache size allows reading more messages into the cache or if there are
     * blocks that can be evicted.
     * @returns True if more messages can be read, false otherwise.
     */
    canReadMore(): boolean;
}
export { CachingIterableSource };
