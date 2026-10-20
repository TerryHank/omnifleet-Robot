import { RawImage } from "@foxglove/schemas";
import type { RawImageOptions } from "./decodeImage";
import { Image as RosImage } from "../../ros";
export declare class WorkerImageDecoder {
    #private;
    constructor();
    /**
     * Copies `image` to the worker, and transfers the decoded result back to the main thread.
     */
    decode(image: RosImage | RawImage, options: Partial<RawImageOptions>): Promise<ImageData>;
    terminate(): void;
}
