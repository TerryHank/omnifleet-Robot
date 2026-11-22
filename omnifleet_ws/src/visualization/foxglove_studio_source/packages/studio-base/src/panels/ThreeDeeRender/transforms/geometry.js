// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { quat } from "gl-matrix";
export function makePose() {
    return { position: { x: 0, y: 0, z: 0 }, orientation: { x: 0, y: 0, z: 0, w: 1 } };
}
export function xyzrpyToPose(xyz, rpy) {
    const o = quat.fromEuler([0, 0, 0, 1], rpy[0], rpy[1], rpy[2]);
    return {
        position: { x: xyz[0], y: xyz[1], z: xyz[2] },
        orientation: { x: o[0], y: o[1], z: o[2], w: o[3] },
    };
}
// Helper functions for constructing geometry primitives that can be used with
// gl-matrix. These methods are preferred over the gl-matrix equivalents since
// they produce number[] arrays instead of Float32Array, which have less
// precision and are slower (float32 requires upcasting/downcasting to do math
// in JavaScript).
export function vec3Identity() {
    return [0, 0, 0];
}
export function vec3FromValues(x, y, z) {
    return [x, y, z];
}
export function vec3Clone(a) {
    return [a[0], a[1], a[2]];
}
export function quatIdentity() {
    return [0, 0, 0, 1];
}
export function quatFromValues(x, y, z, w) {
    return [x, y, z, w];
}
export function quatClone(q) {
    return [q[0], q[1], q[2], q[3]];
}
export function mat4Identity() {
    return [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1];
}
export function mat4FromValues(m00, m01, m02, m03, m10, m11, m12, m13, m20, m21, m22, m23, m30, m31, m32, m33) {
    return [m00, m01, m02, m03, m10, m11, m12, m13, m20, m21, m22, m23, m30, m31, m32, m33];
}
export function mat4Clone(m) {
    return [
        m[0],
        m[1],
        m[2],
        m[3],
        m[4],
        m[5],
        m[6],
        m[7],
        m[8],
        m[9],
        m[10],
        m[11],
        m[12],
        m[13],
        m[14],
        m[15],
    ];
}
/**
 * Test if two numbers are approximately equal.
 */
export function approxEq(v1, v2, epsilon = 0.00001) {
    return Math.abs(v1 - v2) <= epsilon;
}
/**
 * Test if two quaternions are approximately equal.
 */
export function quatAproxEq(q1, q2) {
    return (approxEq(q1.x, q2.x) && approxEq(q1.y, q2.y) && approxEq(q1.z, q2.z) && approxEq(q1.w, q2.w));
}
/**
 * Test if two poses are approximately equal.
 */
export function poseApproxEq(p1, p2) {
    return (approxEq(p1.position.x, p2.position.x) &&
        approxEq(p1.position.y, p2.position.y) &&
        approxEq(p1.position.z, p2.position.z) &&
        quatAproxEq(p1.orientation, p2.orientation));
}
/**
 * Returns a quaternion representing the rotational component of a
 * transformation matrix. The matrix must not have any scaling applied to it.
 * @param out Quaternion to receive the rotation component
 * @param mat Matrix to be decomposed (input)
 * @param scaling Scaling of the matrix (input)
 * @return out
 */
export function getRotationNoScaling(out, mat) {
    const m11 = mat[0];
    const m12 = mat[1];
    const m13 = mat[2];
    const m21 = mat[4];
    const m22 = mat[5];
    const m23 = mat[6];
    const m31 = mat[8];
    const m32 = mat[9];
    const m33 = mat[10];
    const trace = m11 + m22 + m33;
    let S = 0;
    if (trace > 0) {
        S = Math.sqrt(trace + 1.0) * 2;
        out[3] = 0.25 * S;
        out[0] = (m23 - m32) / S;
        out[1] = (m31 - m13) / S;
        out[2] = (m12 - m21) / S;
    }
    else if (m11 > m22 && m11 > m33) {
        S = Math.sqrt(1.0 + m11 - m22 - m33) * 2;
        out[3] = (m23 - m32) / S;
        out[0] = 0.25 * S;
        out[1] = (m12 + m21) / S;
        out[2] = (m31 + m13) / S;
    }
    else if (m22 > m33) {
        S = Math.sqrt(1.0 + m22 - m11 - m33) * 2;
        out[3] = (m31 - m13) / S;
        out[0] = (m12 + m21) / S;
        out[1] = 0.25 * S;
        out[2] = (m23 + m32) / S;
    }
    else {
        S = Math.sqrt(1.0 + m33 - m11 - m22) * 2;
        out[3] = (m12 - m21) / S;
        out[0] = (m31 + m13) / S;
        out[1] = (m23 + m32) / S;
        out[2] = 0.25 * S;
    }
    return out;
}
