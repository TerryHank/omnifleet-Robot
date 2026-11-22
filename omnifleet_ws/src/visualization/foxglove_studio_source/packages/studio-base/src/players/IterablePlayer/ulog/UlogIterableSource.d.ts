import { MessageEvent } from "@foxglove/studio";
import { IIterableSource, IteratorResult, Initalization, MessageIteratorArgs, GetBackfillMessagesArgs } from "../IIterableSource";
type UlogOptions = {
    type: "file";
    file: File;
};
export declare class UlogIterableSource implements IIterableSource {
    #private;
    constructor(options: UlogOptions);
    initialize(): Promise<Initalization>;
    messageIterator(args: MessageIteratorArgs): AsyncIterableIterator<Readonly<IteratorResult>>;
    getBackfillMessages(_args: GetBackfillMessagesArgs): Promise<MessageEvent[]>;
}
export {};
