import { ObjectPool } from "@foxglove/den/collection";
import { CoordinateFrame, FallbackFrameId, AnyFrameId } from "./CoordinateFrame";
import { Transform } from "./Transform";
import { Pose } from "./geometry";
import { Duration, Time } from "./time";
/**
 * Defines the maximum number of transforms across time stored in a single
 * `CoordinateFrame`.
 * We store a history of transforms received so that Markers and other 3D elements
 * can reference the state of a CoordinateFrame transform at a particular time rather than
 * only storing the most recent frame.
 * Considerations for the setting of this value are:
 *  - the larger the value, the more memory is used per panel
 *  - the larger the value, the longer it can take to set transforms within the history
 *  - the larger the value, the more likely it is that objects will be able to reference transforms at older times.
 *    Note that this is highly dependent on the frequency transforms for a given frame are published.
 *    For example, for 50Hz transforms for a single frame and a value of 5,000 max capacity. The transform
 *    history will contain 100 seconds of history for this frame.
 *    For 1kHz transforms for a single frame and a value of 5,000 max capacity. The transform history would
 *    only store 5 seconds of history for this frame.
 *    If the object references a transform at a time older than the history, it will simply use the oldest transform for that frame
 *    which is not guaranteed to be accurate.
 *
 * We generally want to keep this higher to allow for larger transform histories, but
 * also want to be mindful to memory and performance concerns when doing so
 *
 * This number is mentioned in the docs. If changed docs must be updated.
 */
export declare const DEFAULT_MAX_CAPACITY_PER_FRAME = 10000;
export declare enum AddTransformResult {
    NOT_UPDATED = 0,
    UPDATED = 1,
    CYCLE_DETECTED = 2
}
/**
 * TransformTree is a collection of coordinate frames with convenience methods
 * for getting and creating frames and adding transforms between frames.
 */
export declare class TransformTree {
    #private;
    defaultRootFrame: CoordinateFrame<FallbackFrameId>;
    constructor(transformPool: ObjectPool<Transform>, maxStorageTime?: bigint, maxCapacityPerFrame?: number);
    addTransform(frameId: string, parentFrameId: string, time: Time, transform: Transform): AddTransformResult;
    /**
     * Removes transform data from a particular parent-child link at the given timestamp. Does nothing
     * if the child does not exist or has a different parent.
     */
    removeTransform(childFrameId: string, parentFrameId: string, stamp: bigint): void;
    clear(): void;
    clearAfter(time: Time): void;
    hasFrame(id: AnyFrameId): boolean;
    frame<ID extends AnyFrameId>(id: ID): CoordinateFrame<ID> | undefined;
    getOrCreateFrame(id: string): CoordinateFrame;
    frames(): ReadonlyMap<string, CoordinateFrame>;
    apply(output: Pose, input: Readonly<Pose>, frameId: AnyFrameId, rootFrameId: AnyFrameId | undefined, srcFrameId: AnyFrameId, dstTime: Time, srcTime: Time, maxDelta?: Duration): Pose | undefined;
    frameList(): {
        label: string;
        value: string;
    }[];
    /** Get heuristically most valid follow frame Id */
    getDefaultFollowFrameId(): string | undefined;
    static Clone(tree: TransformTree): TransformTree;
}
