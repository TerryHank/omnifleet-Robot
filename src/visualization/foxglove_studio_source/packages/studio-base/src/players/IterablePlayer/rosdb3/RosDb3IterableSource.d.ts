import { MessageEvent } from "@foxglove/studio";
import { IIterableSource, IteratorResult, Initalization, MessageIteratorArgs, GetBackfillMessagesArgs } from "../IIterableSource";
export declare class RosDb3IterableSource implements IIterableSource {
    #private;
    constructor(files: File[]);
    initialize(): Promise<Initalization>;
    messageIterator(opt: MessageIteratorArgs): AsyncIterableIterator<Readonly<IteratorResult>>;
    getBackfillMessages(_args: GetBackfillMessagesArgs): Promise<MessageEvent[]>;
}
