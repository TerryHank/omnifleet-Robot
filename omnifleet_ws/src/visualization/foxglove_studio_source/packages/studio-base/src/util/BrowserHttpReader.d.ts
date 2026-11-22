import { FileReader, FileStream } from "@foxglove/studio-base/util/CachedFilelike";
export default class BrowserHttpReader implements FileReader {
    #private;
    constructor(url: string);
    open(): Promise<{
        size: number;
        identifier?: string;
    }>;
    fetch(offset: number, length: number): FileStream;
}
