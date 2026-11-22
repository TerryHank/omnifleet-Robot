import { Filelike } from "@foxglove/rosbag";
export type FileStream = {
    on<T>(event: "data", listener: (chunk: T) => void): void;
    on(event: "error", listener: (err: Error) => void): void;
    destroy: () => void;
};
export interface FileReader {
    open(): Promise<{
        size: number;
    }>;
    fetch(offset: number, length: number): FileStream;
}
interface ILogger {
    debug(..._args: unknown[]): void;
    info(..._args: unknown[]): void;
    warn(..._args: unknown[]): void;
    error(..._args: unknown[]): void;
}
export default class CachedFilelike implements Filelike {
    #private;
    constructor(options: {
        fileReader: FileReader;
        cacheSizeInBytes?: number;
        log?: ILogger;
        keepReconnectingCallback?: (reconnecting: boolean) => void;
    });
    open(): Promise<void>;
    size(): number;
    read(offset: number, length: number): Promise<Uint8Array>;
}
export {};
