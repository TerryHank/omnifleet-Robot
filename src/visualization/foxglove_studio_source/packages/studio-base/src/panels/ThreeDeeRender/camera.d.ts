import type { ColorRGBA, Vector3 } from "./ros";
import type { Pose } from "./transforms";
export type BaseShape = {
    pose: Pose;
    scale: Vector3;
    color?: ColorRGBA;
};
export type MouseEventObject = {
    object: BaseShape;
    instanceIndex?: number;
};
export type CameraState = {
    distance: number;
    perspective: boolean;
    phi: number;
    target: readonly [number, number, number];
    targetOffset: readonly [number, number, number];
    targetOrientation: readonly [number, number, number, number];
    thetaOffset: number;
    fovy: number;
    near: number;
    far: number;
};
export declare const DEFAULT_CAMERA_STATE: CameraState;
