import { RawImage } from "@foxglove/schemas";
import { CompressedImageTypes } from "./ImageTypes";
import { Image as RosImage } from "../../ros";
import { ColorModeSettings } from "../colorMode";
export declare function decodeCompressedImageToBitmap(image: CompressedImageTypes, resizeWidth?: number): Promise<ImageBitmap>;
export declare const IMAGE_DEFAULT_COLOR_MODE_SETTINGS: Required<Omit<ColorModeSettings, "colorField" | "minValue" | "maxValue">>;
export type RawImageOptions = ColorModeSettings;
/**
 * See also:
 * https://github.com/ros2/common_interfaces/blob/366eea24ffce6c87f8860cbcd27f4863f46ad822/sensor_msgs/include/sensor_msgs/image_encodings.hpp
 */
export declare function decodeRawImage(image: RosImage | RawImage, options: Partial<RawImageOptions>, output: Uint8ClampedArray): void;
