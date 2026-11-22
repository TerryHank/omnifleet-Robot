import { Time } from "@foxglove/rostime";
import { CompressedImage, RawImage } from "@foxglove/schemas";
import { Image as RosImage, CompressedImage as RosCompressedImage } from "../../ros";
export declare const ALL_CAMERA_INFO_SCHEMAS: Set<string>;
export type CompressedImageTypes = RosCompressedImage | CompressedImage;
export type AnyImage = RosImage | RosCompressedImage | RawImage | CompressedImage;
export declare function getFrameIdFromImage(image: AnyImage): string;
export declare function getTimestampFromImage(image: AnyImage): Time;
