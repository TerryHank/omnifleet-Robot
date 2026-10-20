// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { mat4, vec3, quat } from "gl-matrix";
import { getRotationNoScaling, mat4Identity, quatIdentity, vec3Identity } from "./geometry";
/**
 * Transform represents a position and rotation in 3D space. It can be set and
 * accessed using either Vec3/Quat or Mat4, and these different representations
 * are automatically kept in sync.
 */
export class Transform {
    #position;
    #rotation;
    #matrix;
    constructor(matrixOrPosition, rotation) {
        if (matrixOrPosition == undefined) {
            this.#position = [0, 0, 0];
            this.#rotation = [0, 0, 0, 1];
            quat.normalize(this.#rotation, this.#rotation);
            this.#matrix = mat4.fromRotationTranslation(mat4Identity(), this.#rotation, this.#position);
        }
        else if (matrixOrPosition.length === 16) {
            this.#matrix = matrixOrPosition;
            this.#position = [0, 0, 0];
            this.#rotation = [0, 0, 0, 1];
            mat4.getTranslation(this.#position, this.#matrix);
            getRotationNoScaling(this.#rotation, this.#matrix);
        }
        else if (matrixOrPosition.length === 3 && rotation != undefined) {
            this.#position = matrixOrPosition;
            this.#rotation = rotation;
            quat.normalize(this.#rotation, this.#rotation);
            this.#matrix = mat4.fromRotationTranslation(mat4Identity(), this.#rotation, this.#position);
        }
        else {
            throw new Error(`new Transform() expected either mat4 or vec3 + quat`);
        }
    }
    position() {
        return this.#position;
    }
    rotation() {
        return this.#rotation;
    }
    matrix() {
        return this.#matrix;
    }
    setPosition(position) {
        vec3.copy(this.#position, position);
        mat4.fromRotationTranslation(this.#matrix, this.#rotation, this.#position);
        return this;
    }
    setRotation(rotation) {
        quat.normalize(this.#rotation, rotation);
        mat4.fromRotationTranslation(this.#matrix, this.#rotation, this.#position);
        return this;
    }
    /**
     * Update position and rotation simultaneously. This is more efficient than
     * calling setPosition and setRotation separately, since we only need to
     * update the matrix once
     */
    setPositionRotation(position, rotation) {
        vec3.copy(this.#position, position);
        quat.normalize(this.#rotation, rotation);
        mat4.fromRotationTranslation(this.#matrix, this.#rotation, this.#position);
        return this;
    }
    /**
     * Update position and rotation from a Pose object
     */
    setPose(pose) {
        vec3.set(this.#position, pose.position.x, pose.position.y, pose.position.z);
        quat.set(this.#rotation, pose.orientation.x, pose.orientation.y, pose.orientation.z, pose.orientation.w);
        quat.normalize(this.#rotation, this.#rotation);
        mat4.fromRotationTranslation(this.#matrix, this.#rotation, this.#position);
        return this;
    }
    /**
     * Update position and rotation from a matrix with unit scale
     */
    setMatrixUnscaled(matrix) {
        mat4.copy(this.#matrix, matrix);
        mat4.getTranslation(this.#position, matrix);
        getRotationNoScaling(this.#rotation, matrix); // A faster mat4.getRotation when there is no scaling
        return this;
    }
    /**
     * Copy the values in another transform into this one
     */
    copy(other) {
        vec3.copy(this.#position, other.#position);
        quat.copy(this.#rotation, other.#rotation);
        mat4.copy(this.#matrix, other.#matrix);
        return this;
    }
    toPose(out) {
        out.position.x = this.#position[0];
        out.position.y = this.#position[1];
        out.position.z = this.#position[2];
        out.orientation.x = this.#rotation[0];
        out.orientation.y = this.#rotation[1];
        out.orientation.z = this.#rotation[2];
        out.orientation.w = this.#rotation[3];
    }
    static Identity() {
        return new Transform(vec3Identity(), quatIdentity());
    }
    static Empty() {
        return new Transform();
    }
    /**
     * Interpolate between two rigid body transforms using linear interpolation on
     * the translation vector and spherical linear interpolation on the rotation
     * quaternion.
     *
     * @param out Output transform to store the result in
     * @param a Start transform
     * @param b End transform
     * @param t Interpolant in the range [0, 1]
     * @returns A reference to `out`
     */
    static Interpolate(out, a, b, t) {
        vec3.lerp(out.#position, a.position(), b.position(), t);
        quat.slerp(out.#rotation, a.rotation(), b.rotation(), t);
        out.setPositionRotation(out.#position, out.#rotation);
        return out;
    }
}
