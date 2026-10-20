import { MessageEvent } from "@foxglove/studio-base/players/types";
import { IIterableSource, IteratorResult, Initalization, MessageIteratorArgs, GetBackfillMessagesArgs } from "./IIterableSource";
type BagSource = {
    type: "file";
    file: File;
} | {
    type: "remote";
    url: string;
};
export declare class BagIterableSource implements IIterableSource {
    #private;
    constructor(source: BagSource);
    initialize(): Promise<Initalization>;
    messageIterator(opt: MessageIteratorArgs): AsyncIterableIterator<Readonly<IteratorResult>>;
    getBackfillMessages({ topics, time, }: GetBackfillMessagesArgs): Promise<MessageEvent[]>;
}
export {};
