import { vec3, quat, mat4, ReadonlyMat4 } from "gl-matrix";
export type Point = {
    x: number;
    y: number;
    z: number;
};
export type Orientation = {
    x: number;
    y: number;
    z: number;
    w: number;
};
export type Pose = {
    position: Point;
    orientation: Orientation;
};
export declare function makePose(): Pose;
export declare function xyzrpyToPose(xyz: vec3, rpy: vec3): Pose;
export declare function vec3Identity(): vec3;
export declare function vec3FromValues(x: number, y: number, z: number): vec3;
export declare function vec3Clone(a: vec3): vec3;
export declare function quatIdentity(): quat;
export declare function quatFromValues(x: number, y: number, z: number, w: number): quat;
export declare function quatClone(q: quat): quat;
export declare function mat4Identity(): mat4;
export declare function mat4FromValues(m00: number, m01: number, m02: number, m03: number, m10: number, m11: number, m12: number, m13: number, m20: number, m21: number, m22: number, m23: number, m30: number, m31: number, m32: number, m33: number): mat4;
export declare function mat4Clone(m: mat4): mat4;
/**
 * Test if two numbers are approximately equal.
 */
export declare function approxEq(v1: number, v2: number, epsilon?: number): boolean;
/**
 * Test if two quaternions are approximately equal.
 */
export declare function quatAproxEq(q1: Orientation, q2: Orientation): boolean;
/**
 * Test if two poses are approximately equal.
 */
export declare function poseApproxEq(p1: Pose, p2: Pose): boolean;
/**
 * Returns a quaternion representing the rotational component of a
 * transformation matrix. The matrix must not have any scaling applied to it.
 * @param out Quaternion to receive the rotation component
 * @param mat Matrix to be decomposed (input)
 * @param scaling Scaling of the matrix (input)
 * @return out
 */
export declare function getRotationNoScaling(out: quat, mat: ReadonlyMat4): quat;
