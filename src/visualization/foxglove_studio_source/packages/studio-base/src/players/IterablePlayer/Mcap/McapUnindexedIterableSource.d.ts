import { MessageEvent } from "@foxglove/studio";
import { GetBackfillMessagesArgs, IIterableSource, Initalization, IteratorResult, MessageIteratorArgs } from "@foxglove/studio-base/players/IterablePlayer/IIterableSource";
type Options = {
    size: number;
    stream: ReadableStream<Uint8Array>;
};
/** Only efficient for small files */
export declare class McapUnindexedIterableSource implements IIterableSource {
    #private;
    constructor(options: Options);
    initialize(): Promise<Initalization>;
    messageIterator(args: MessageIteratorArgs): AsyncIterableIterator<Readonly<IteratorResult>>;
    getBackfillMessages(args: GetBackfillMessagesArgs): Promise<MessageEvent[]>;
}
export {};
