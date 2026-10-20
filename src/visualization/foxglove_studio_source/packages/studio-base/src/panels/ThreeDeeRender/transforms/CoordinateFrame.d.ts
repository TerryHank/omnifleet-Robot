import { mat4, vec3 } from "gl-matrix";
import { ObjectPool } from "@foxglove/den/collection/ObjectPool";
import { Transform } from "./Transform";
import { Pose } from "./geometry";
import { Duration, Time } from "./time";
type TimeAndTransform = [time: Time, transform: Transform];
export declare const MAX_DURATION: Duration;
export declare const MAX_CAPACITY_EVICT_PORTION = 0.25;
declare const FALLBACK_FRAME_ID: unique symbol;
export type FallbackFrameId = typeof FALLBACK_FRAME_ID;
export type UserFrameId = string;
export type AnyFrameId = UserFrameId | FallbackFrameId;
/**
 * CoordinateFrame is a named 3D coordinate frame with an optional parent frame
 * and a history of transforms from this frame to its parent. The parent/child
 * hierarchy and transform history allow points to be transformed from one
 * coordinate frame to another while interpolating over time.
 */
export declare class CoordinateFrame<ID extends AnyFrameId = UserFrameId> {
    #private;
    static readonly FALLBACK_FRAME_ID: FallbackFrameId;
    readonly id: ID;
    maxStorageTime: Duration;
    maxCapacity: number;
    offsetPosition: vec3 | undefined;
    offsetEulerDegrees: vec3 | undefined;
    constructor(id: ID, parent: CoordinateFrame | undefined, // fallback frame not allowed as parent
    maxStorageTime: Duration, maxCapacity: number, transformPool: ObjectPool<Transform>);
    static assertUserFrame(frame: CoordinateFrame<AnyFrameId>): asserts frame is CoordinateFrame;
    parent(): CoordinateFrame | undefined;
    /**
     * Returns the top-most frame by walking up each parent frame. If the current
     * frame does not have a parent, the current frame is returned.
     */
    root(): CoordinateFrame<ID>;
    /**
     * Returns true if this frame has no parent frame.
     */
    isRoot(): boolean;
    /**
     * Returns the number of transforms stored in the transform history.
     */
    transformsSize(): number;
    /**
     * Set the parent frame for this frame. If the parent frame is already set to
     * a different frame, the transform history is cleared.
     */
    setParent(parent: CoordinateFrame): void;
    /**
     * Search for an ancestor frame with the given ID by walking up the chain of
     * parent frames, starting at the current frame.
     * @param id Frame ID to search for
     * @returns The ancestor frame, or undefined if not found
     */
    findAncestor(id: string): CoordinateFrame | undefined;
    /**
     * Add a transform to the transform history maintained by this frame. When the maximum capacity
     * has been reached, the history is trimmed by removing the larger portion of either
     * frames that are outside of the `maxStorageTime` or the last quarter of oldest frames.
     * This is to amortize the cost of trimming the history ever time a new transform is added.
     *
     * If a transform with an identical timestamp already exists, it is replaced.
     */
    addTransform(time: Time, transform: Transform): void;
    /** Remove all transforms with timestamps greater than the given timestamp. */
    removeTransformsAfter(time: Time): void;
    /** Removes a transform with a specific timestamp */
    removeTransformAt(time: Time): void;
    /**
     * Find the closest transform(s) in the transform history to the given time.
     * Note that if an exact match is found, both `outLower` and `outUpper` will
     * be set to the same transform.
     * @param outLower This will be set to the found transform with the closest
     *   timestamp <= the given time
     * @param outUpper This will be set to the found transform with the closest
     *   timestamp >= the given time
     * @param time Time to search for
     * @param maxDelta The time parameter can exceed the bounds of the transform
     *   history by up to this amount and still clamp to the oldest or newest
     *   transform
     * @returns True if the search was successful
     */
    findClosestTransforms(outLower: TimeAndTransform, outUpper: TimeAndTransform, time: Time, maxDelta: Duration): boolean;
    /**
     * Transform a pose from the coordinate frame `srcFrame` to this coordinate
     * frame at the given time. The transform will be done using the shortest path
     * from `srcFrame` to this frame
     *
     * Transforms can go up through multiple parents, down through one or more
     * children, or both as long as the transforms share a common ancestor.
     *
     * A common variable naming convention for the returned pose is
     * `thisFrame_T_srcFrame` which is read right-to-left as "the translation that
     * moves a point from `srcFrame` to `thisFrame`".
     * @param out Output pose, this will be modified with the result on success
     * @param input Input pose that exists in `srcFrame`
     * @param srcFrame Coordinate frame we are transforming from
     * @param time Time to compute the transform at
     * @param maxDelta The time parameter can exceed the bounds of the transform
     *   history by up to this amount and still clamp to the oldest or newest
     *   transform
     * @returns A reference to `out` on success, otherwise undefined
     */
    applyLocal(out: Pose, input: Readonly<Pose>, srcFrame: CoordinateFrame<AnyFrameId>, time: Time, maxDelta?: Duration): Pose | undefined;
    /**
     * Transform a pose from the coordinate frame `srcFrame` to rootFrame at
     * `srcTime`, then from `rootFrame` to this coordinate frame at `dstTime`. The
     * transform will be done using the shortest path from `srcFrame` to the root
     * frame, then from the root frame to this frame.
     *
     * Transforms can go up through multiple parents, down through one or more
     * children, or both as long as the transforms share a common ancestor.
     * @param out Output pose, this will be modified with the result on success
     * @param input Input pose that exists in `srcFrame`
     * @param rootFrame Reference coordinate frame to transform from srcFrame into as srcTime
     * @param srcFrame Coordinate frame we are transforming from
     * @param dstTime Time to transform from rootFrome into this frame
     * @param srcTime Time to transform from srcFrame into rootFrame
     * @param maxDelta The time parameter can exceed the bounds of the transform
     *   history by up to this amount and still clamp to the oldest or newest
     *   transform
     * @returns A reference to `out` on success, otherwise undefined
     */
    apply(out: Pose, input: Readonly<Pose>, rootFrame: CoordinateFrame<AnyFrameId>, srcFrame: CoordinateFrame<AnyFrameId>, dstTime: Time, srcTime: Time, maxDelta?: Duration): Pose | undefined;
    /**
     * Returns a display-friendly rendition of `id`, quoting the frame id if it is
     * an empty string or starts or ends with whitespace.
     */
    displayName(): string;
    /**
     * Interpolate between two [time, transform] pairs.
     * @param output Output parameter for the interpolated time and transform
     * @param lower Start [time, transform]
     * @param upper End [time, transform]
     * @param time Interpolant in the range [lower[0], upper[0]]
     */
    static Interpolate(output: TimeAndTransform, lower: TimeAndTransform, upper: TimeAndTransform, time: Time): void;
    /**
     * Interpolate the transform between two [time, transform] pairs.
     * @param output Output parameter for the interpolated transform
     * @param lower Start [time, transform]
     * @param upper End [time, transform]
     * @param time Interpolant in the range [lower[0], upper[0]]
     */
    static InterpolateTransform(output: Transform, lower: TimeAndTransform, upper: TimeAndTransform, time: Time): void;
    /**
     * Get the transform `parentFrame_T_childFrame` (from child to parent) at the
     * given time.
     * @param out Output transform matrix
     * @param parentFrame Parent destination frame
     * @param childFrame Child source frame
     * @param time Time to transform at
     * @param maxDelta The time parameter can exceed the bounds of the transform
     *   history by up to this amount and still clamp to the oldest or newest
     *   transform
     * @returns True on success
     */
    static GetTransformMatrix(out: mat4, parentFrame: CoordinateFrame, childFrame: CoordinateFrame, time: Time, maxDelta: Duration): boolean;
    /**
     * Apply the transform from `child` to `parent` at the given time to the given
     * input pose. The transform can optionally be inverted, to go from `parent`
     * to `child`.
     * @param out Output pose, this will be modified with the result on success
     * @param input Input pose that exists in `child`, or `parent` if `invert` is
     *   true
     * @param parent Parent frame
     * @param child Child frame
     * @invert Whether to invert the transform (go from parent to child)
     * @param time Time to compute the transform at
     * @param maxDelta The time parameter can exceed the bounds of the transform
     *   history by up to this amount and still clamp to the oldest or newest
     *   transform
     * @returns True on success
     */
    static Apply(out: Pose, input: Readonly<Pose>, parent: CoordinateFrame, child: CoordinateFrame, invert: boolean, time: Time, maxDelta: Duration): boolean;
    /**
     * Returns a display-friendly rendition of `frameId`, quoting the id if it is
     * an empty string or starts or ends with whitespace.
     */
    static DisplayName(frameId: AnyFrameId): string;
}
export {};
