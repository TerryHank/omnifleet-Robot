export declare class BlobReadable {
    private file;
    constructor(file: Blob);
    size(): Promise<bigint>;
    read(offset: bigint, size: bigint): Promise<Uint8Array>;
}
