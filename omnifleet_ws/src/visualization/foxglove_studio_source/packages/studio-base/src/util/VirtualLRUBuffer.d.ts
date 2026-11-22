import { Range } from "./ranges";
export default class VirtualLRUBuffer {
    #private;
    readonly byteLength: number;
    constructor(options: {
        size: number;
        blockSize?: number;
        numberOfBlocks?: number;
    });
    hasData(start: number, end: number): boolean;
    getRangesWithData(): Range[];
    copyFrom(source: Uint8Array, targetStart: number): void;
    slice(start: number, end: number): Uint8Array;
}
