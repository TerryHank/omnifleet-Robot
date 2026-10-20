export declare class RemoteFileReadable {
    #private;
    constructor(url: string);
    open(): Promise<void>;
    size(): Promise<bigint>;
    read(offset: bigint, size: bigint): Promise<Uint8Array>;
}
