import { Time } from "@foxglove/studio";
import type { IMessageCursor, IteratorResult } from "./IIterableSource";
declare class IteratorCursor implements IMessageCursor {
    #private;
    constructor(iterator: AsyncIterableIterator<Readonly<IteratorResult>>, abort?: AbortSignal);
    next(): ReturnType<IMessageCursor["next"]>;
    nextBatch(durationMs: number): Promise<IteratorResult[] | undefined>;
    readUntil(end: Time): ReturnType<IMessageCursor["readUntil"]>;
    end(): ReturnType<IMessageCursor["end"]>;
}
export { IteratorCursor };
