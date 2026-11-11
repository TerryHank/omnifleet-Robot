import { mat4, vec3, quat, ReadonlyMat4, ReadonlyVec3, ReadonlyQuat } from "gl-matrix";
import { Pose } from "./geometry";
/**
 * Transform represents a position and rotation in 3D space. It can be set and
 * accessed using either Vec3/Quat or Mat4, and these different representations
 * are automatically kept in sync.
 */
export declare class Transform {
    #private;
    constructor(matrixOrPosition?: mat4 | vec3, rotation?: quat);
    position(): ReadonlyVec3;
    rotation(): ReadonlyQuat;
    matrix(): ReadonlyMat4;
    setPosition(position: ReadonlyVec3): this;
    setRotation(rotation: ReadonlyQuat): this;
    /**
     * Update position and rotation simultaneously. This is more efficient than
     * calling setPosition and setRotation separately, since we only need to
     * update the matrix once
     */
    setPositionRotation(position: vec3, rotation: quat): this;
    /**
     * Update position and rotation from a Pose object
     */
    setPose(pose: Readonly<Pose>): this;
    /**
     * Update position and rotation from a matrix with unit scale
     */
    setMatrixUnscaled(matrix: ReadonlyMat4): this;
    /**
     * Copy the values in another transform into this one
     */
    copy(other: Transform): this;
    toPose(out: Pose): void;
    static Identity(): Transform;
    static Empty(): Transform;
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
    static Interpolate(out: Transform, a: Transform, b: Transform, t: number): Transform;
}
