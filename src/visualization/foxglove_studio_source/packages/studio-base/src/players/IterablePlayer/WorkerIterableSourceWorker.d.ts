import * as Comlink from "comlink";
import { Immutable, MessageEvent } from "@foxglove/studio";
import type { GetBackfillMessagesArgs, IIterableSource, IMessageCursor, Initalization, IteratorResult, MessageIteratorArgs } from "./IIterableSource";
export declare class WorkerIterableSourceWorker implements IIterableSource {
    protected _source: IIterableSource;
    constructor(source: IIterableSource);
    initialize(): Promise<Initalization>;
    messageIterator(args: MessageIteratorArgs): AsyncIterableIterator<Readonly<IteratorResult>> & Comlink.ProxyMarked;
    getBackfillMessages(args: Omit<GetBackfillMessagesArgs, "abortSignal">, abortSignal?: AbortSignal): Promise<MessageEvent[]>;
    getMessageCursor(args: Omit<Immutable<MessageIteratorArgs>, "abort">, abort?: AbortSignal): IMessageCursor & Comlink.ProxyMarked;
}
