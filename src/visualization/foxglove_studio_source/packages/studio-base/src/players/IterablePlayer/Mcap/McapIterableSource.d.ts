import { MessageEvent } from "@foxglove/studio-base/players/types";
import { IIterableSource, IteratorResult, Initalization, MessageIteratorArgs, GetBackfillMessagesArgs } from "../IIterableSource";
type McapSource = {
    type: "file";
    file: Blob;
} | {
    type: "url";
    url: string;
};
export declare class McapIterableSource implements IIterableSource {
    #private;
    constructor(source: McapSource);
    initialize(): Promise<Initalization>;
    messageIterator(opt: MessageIteratorArgs): AsyncIterableIterator<Readonly<IteratorResult>>;
    getBackfillMessages(args: GetBackfillMessagesArgs): Promise<MessageEvent[]>;
}
export {};
