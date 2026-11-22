import { CAMERA_CALIBRATION_DATATYPES } from "@foxglove/studio-base/panels/ThreeDeeRender/foxglove";
import { CAMERA_INFO_DATATYPES, } from "../../ros";
export const ALL_CAMERA_INFO_SCHEMAS = new Set([
    ...CAMERA_INFO_DATATYPES,
    ...CAMERA_CALIBRATION_DATATYPES,
]);
export function getFrameIdFromImage(image) {
    if ("header" in image) {
        return image.header.frame_id;
    }
    else {
        return image.frame_id;
    }
}
export function getTimestampFromImage(image) {
    if ("header" in image) {
        return image.header.stamp;
    }
    else {
        return image.timestamp;
    }
}
