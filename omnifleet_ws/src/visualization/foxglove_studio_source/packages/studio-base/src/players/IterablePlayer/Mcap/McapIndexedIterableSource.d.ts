import { McapIndexedReader } from "@mcap/core";
import { MessageEvent } from "@foxglove/studio";
import { GetBackfillMessagesArgs, IIterableSource, Initalization, IteratorResult, MessageIteratorArgs } from "@foxglove/studio-base/players/IterablePlayer/IIterableSource";
export declare class McapIndexedIterableSource implements IIterableSource {
    #private;
    constructor(reader: McapIndexedReader);
    initialize(): Promise<Initalization>;
    messageIterator(args: MessageIteratorArgs): AsyncIterableIterator<Readonly<IteratorResult>>;
    getBackfillMessages(args: GetBackfillMessagesArgs): Promise<MessageEvent[]>;
}
