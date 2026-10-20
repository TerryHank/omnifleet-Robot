import { CameraCalibration, CompressedImage, RawImage } from "@foxglove/schemas";
import { MessageEvent } from "@foxglove/studio";
type MakeImageArgs = {
    width: number;
    height: number;
    frameId: string;
    imageTopic: string;
    calibrationTopic: string;
    fx?: number;
    fy?: number;
};
export declare function makeRawImageAndCalibration(args: MakeImageArgs): {
    calibrationMessage: MessageEvent<Partial<CameraCalibration>>;
    cameraMessage: MessageEvent<Partial<RawImage>>;
};
export declare function makeCompressedImageAndCalibration(args: MakeImageArgs): Promise<{
    calibrationMessage: MessageEvent<Partial<CameraCalibration>>;
    cameraMessage: MessageEvent<Partial<CompressedImage>>;
}>;
export {};
