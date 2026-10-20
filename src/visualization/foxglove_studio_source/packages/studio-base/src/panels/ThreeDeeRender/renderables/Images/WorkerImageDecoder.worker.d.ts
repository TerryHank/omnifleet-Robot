import type { RawImage } from "@foxglove/schemas";
import { RawImageOptions } from "./decodeImage";
import type { Image as RosImage } from "../../ros";
declare function decode(image: RosImage | RawImage, options: Partial<RawImageOptions>): ImageData;
export declare const service: {
    decode: typeof decode;
};
export {};
