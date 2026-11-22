import { Immutable, MessageEvent } from "@foxglove/studio";
import type { GetBackfillMessagesArgs, IIterableSource, IMessageCursor, Initalization, IteratorResult, MessageIteratorArgs, IterableSourceInitializeArgs } from "./IIterableSource";
type ConstructorArgs = {
    initWorker: () => Worker;
    initArgs: IterableSourceInitializeArgs;
};
export declare class WorkerIterableSource implements IIterableSource {
    #private;
    constructor(args: ConstructorArgs);
    initialize(): Promise<Initalization>;
    messageIterator(args: MessageIteratorArgs): AsyncIterableIterator<Readonly<IteratorResult>>;
    getBackfillMessages(args: GetBackfillMessagesArgs): Promise<MessageEvent[]>;
    getMessageCursor(args: Immutable<MessageIteratorArgs & {
        abort?: AbortSignal;
    }>): IMessageCursor;
    terminate(): Promise<void>;
}
export {};
