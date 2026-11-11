import type { Immutable as Im, MessageEvent } from "@foxglove/studio";
import type { MessageBlock } from "@foxglove/studio-base/players/types";
/**
 * BlockTopicProcessor adds alias messages to blocks.
 *
 * It tries to keep referential stability for aliased messages by tracking the input messages on the
 * original topic and storing the aliased message arrays to return them if the input messages are
 * unchanged.
 */
export declare class BlockTopicProcessor {
    #private;
    constructor(originalTopic: string, aliases: Im<string[]>);
    /**
     * Alias the block and return the aliased messages by topic. The aliases and the input messages
     * are stored so if the block has already been aliased and is unchanged, then the existing aliased
     * messages by topic are returned.
     */
    aliasBlock(block: Im<MessageBlock>, index: number): Record<string, MessageEvent[]>;
}
