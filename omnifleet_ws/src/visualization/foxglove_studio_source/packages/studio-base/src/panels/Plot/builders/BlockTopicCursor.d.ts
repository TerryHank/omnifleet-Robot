import { Immutable, MessageEvent } from "@foxglove/studio";
import { MessageBlock } from "@foxglove/studio-base/players/types";
/**
 * BlockTopicCursor tracks the last seen block messages for a given topic and can produce the next
 * block that has not yet been processed.
 *
 * When block topic data changes, it re-starts _next_.
 */
export declare class BlockTopicCursor {
    #private;
    constructor(topic: string);
    /**
     * Return true if the cursor is invalidated and reading next will start from the beginning
     */
    nextWillReset(blocks: Immutable<(MessageBlock | undefined)[]>): boolean;
    /**
     * Given an array of blocks, return the next set of messages.
     *
     * When the underlying topic data changes, the cursor is reset.
     */
    next(blocks: Immutable<(MessageBlock | undefined)[]>): Immutable<MessageEvent[]> | undefined;
}
