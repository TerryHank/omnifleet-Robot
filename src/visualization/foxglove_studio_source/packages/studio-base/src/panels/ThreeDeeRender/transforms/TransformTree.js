// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { CoordinateFrame, MAX_DURATION } from "./CoordinateFrame";
import { Transform } from "./Transform";
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
export const DEFAULT_MAX_CAPACITY_PER_FRAME = 10000;
export var AddTransformResult;
(function (AddTransformResult) {
    AddTransformResult[AddTransformResult["NOT_UPDATED"] = 0] = "NOT_UPDATED";
    AddTransformResult[AddTransformResult["UPDATED"] = 1] = "UPDATED";
    AddTransformResult[AddTransformResult["CYCLE_DETECTED"] = 2] = "CYCLE_DETECTED";
})(AddTransformResult || (AddTransformResult = {}));
// Coordinate frames named in [REP-105](https://www.ros.org/reps/rep-0105.html)
const DEFAULT_FRAME_IDS = ["base_link", "odom", "map", "earth"];
/**
 * TransformTree is a collection of coordinate frames with convenience methods
 * for getting and creating frames and adding transforms between frames.
 */
export class TransformTree {
    #frames = new Map();
    #maxStorageTime;
    #maxCapacityPerFrame;
    #transformPool;
    defaultRootFrame;
    constructor(transformPool, maxStorageTime = MAX_DURATION, maxCapacityPerFrame = DEFAULT_MAX_CAPACITY_PER_FRAME) {
        this.#transformPool = transformPool;
        this.#maxStorageTime = maxStorageTime;
        this.#maxCapacityPerFrame = maxCapacityPerFrame;
        this.defaultRootFrame = new CoordinateFrame(CoordinateFrame.FALLBACK_FRAME_ID, undefined, this.#maxStorageTime, this.#maxCapacityPerFrame, this.#transformPool);
        this.defaultRootFrame.addTransform(0n, Transform.Identity());
    }
    addTransform(frameId, parentFrameId, time, transform) {
        let updated = !this.hasFrame(frameId);
        let cycleDetected = false;
        const frame = this.getOrCreateFrame(frameId);
        const curParentFrame = frame.parent();
        if (curParentFrame == undefined || curParentFrame.id !== parentFrameId) {
            cycleDetected = this.#checkParentForCycle(frameId, parentFrameId);
            // This frame was previously unparented but now we know its parent, or we
            // are reparenting this frame
            if (!cycleDetected) {
                frame.setParent(this.getOrCreateFrame(parentFrameId));
                updated = true;
            }
        }
        if (!cycleDetected) {
            frame.addTransform(time, transform);
        }
        return cycleDetected
            ? AddTransformResult.CYCLE_DETECTED
            : updated
                ? AddTransformResult.UPDATED
                : AddTransformResult.NOT_UPDATED;
    }
    /**
     * Removes transform data from a particular parent-child link at the given timestamp. Does nothing
     * if the child does not exist or has a different parent.
     */
    removeTransform(childFrameId, parentFrameId, stamp) {
        const child = this.frame(childFrameId);
        if (!child) {
            return;
        }
        if (child.parent()?.id !== parentFrameId) {
            return;
        }
        child.removeTransformAt(stamp);
        this.#removeEmptyAncestors(child);
    }
    /**
     * Walk up the tree starting from `candidate` and prune frames with no history entries and no
     * children.
     */
    #removeEmptyAncestors(candidate) {
        if (candidate.transformsSize() > 0) {
            // don't want to delete this frame, it is not empty
            return;
        }
        // Build a list of children for each frame in the tree, used to check whether nodes are leaf
        // nodes
        const childrenByParentId = new Map();
        for (const frame of this.#frames.values()) {
            childrenByParentId.set(frame.id, new Set());
        }
        for (const frame of this.#frames.values()) {
            const parent = frame.parent();
            if (parent === candidate) {
                // can't delete this frame or its ancestors, it still has children
                return;
            }
            if (parent == undefined) {
                continue;
            }
            const children = childrenByParentId.get(parent.id);
            if (!children) {
                throw new Error("invariant: should have children array");
            }
            children.add(frame.id);
        }
        // Walk upwards, deleting nodes with no history entries and no children
        for (let current = candidate; current; current = current.parent()) {
            if (current.transformsSize() > 0) {
                // don't want to delete this frame, it is not empty
                return;
            }
            const children = childrenByParentId.get(current.id);
            if (children && children.size > 0) {
                // can't delete this frame or its ancestors, it still has children
                return;
            }
            this.#frames.delete(current.id);
            childrenByParentId.delete(current.id);
            const parentId = current.parent()?.id;
            if (parentId) {
                childrenByParentId.get(parentId)?.delete(current.id);
            }
        }
    }
    clear() {
        this.#frames.clear();
    }
    clearAfter(time) {
        for (const frame of this.#frames.values()) {
            frame.removeTransformsAfter(time);
        }
    }
    hasFrame(id) {
        if (id === CoordinateFrame.FALLBACK_FRAME_ID) {
            return true;
        }
        return this.#frames.has(id);
    }
    frame(id) {
        if (id === CoordinateFrame.FALLBACK_FRAME_ID) {
            return this.defaultRootFrame;
        }
        return this.#frames.get(id);
    }
    getOrCreateFrame(id) {
        let frame = this.#frames.get(id);
        if (!frame) {
            frame = new CoordinateFrame(id, undefined, this.#maxStorageTime, this.#maxCapacityPerFrame, this.#transformPool);
            this.#frames.set(id, frame);
        }
        return frame;
    }
    frames() {
        return this.#frames;
    }
    apply(output, input, frameId, rootFrameId, srcFrameId, dstTime, srcTime, maxDelta) {
        const frame = this.frame(frameId);
        const srcFrame = this.frame(srcFrameId);
        if (!frame || !srcFrame) {
            return undefined;
        }
        const rootFrame = (rootFrameId != undefined ? this.frame(rootFrameId) : frame.root()) ?? frame.root();
        return frame.apply(output, input, rootFrame, srcFrame, dstTime, srcTime, maxDelta);
    }
    frameList() {
        const frames = Array.from(this.#frames.values());
        const frameMap = new Map(frames.map((frame) => [frame.id, { id: frame.id, children: [] }]));
        // Create a hierarchy of coordinate frames
        const rootFrames = [];
        for (const frame of frames) {
            const frameEntry = frameMap.get(frame.id);
            const parentId = frame.parent()?.id;
            if (parentId == undefined) {
                rootFrames.push(frameEntry);
            }
            else {
                const parent = frameMap.get(parentId);
                if (parent == undefined) {
                    continue;
                }
                parent.children.push(frameEntry);
            }
        }
        // Convert the `rootFrames` hierarchy into a flat list of coordinate frames with depth
        const output = [];
        function addFrame(frame, depth) {
            const displayName = CoordinateFrame.DisplayName(frame.id);
            output.push({
                value: frame.id,
                label: `${"\u00A0\u00A0".repeat(depth)}${displayName}`,
            });
            frame.children.sort((a, b) => a.id.localeCompare(b.id));
            for (const child of frame.children) {
                addFrame(child, depth + 1);
            }
        }
        rootFrames.sort((a, b) => a.id.localeCompare(b.id));
        for (const entry of rootFrames) {
            addFrame(entry, 0);
        }
        return output;
    }
    /** Get heuristically most valid follow frame Id */
    getDefaultFollowFrameId() {
        const allFrames = this.frames();
        if (allFrames.size === 0) {
            return undefined;
        }
        // Prefer frames from [REP-105](https://www.ros.org/reps/rep-0105.html)
        for (const frameId of DEFAULT_FRAME_IDS) {
            const frame = this.frame(frameId);
            if (frame) {
                return frame.id;
            }
        }
        // Choose the root frame with the most children
        const rootsToCounts = new Map();
        for (const frame of allFrames.values()) {
            const root = frame.root();
            const rootId = root.id;
            rootsToCounts.set(rootId, (rootsToCounts.get(rootId) ?? 0) + 1);
        }
        const rootsArray = Array.from(rootsToCounts.entries());
        const rootId = rootsArray.sort((a, b) => b[1] - a[1])[0]?.[0];
        return rootId;
    }
    #checkParentForCycle(frameId, parentFrameId) {
        if (frameId === parentFrameId) {
            return true;
        }
        // walk up tree from parent Frame to check if it eventually crosses the frame
        let frame = this.frame(parentFrameId);
        while (frame?.parent()) {
            if (frame.parent()?.id === frameId) {
                return true;
            }
            frame = frame.parent();
        }
        return false;
    }
    static Clone(tree) {
        const newTree = new TransformTree(tree.#transformPool, tree.#maxStorageTime, tree.#maxCapacityPerFrame);
        newTree.#frames = tree.#frames;
        return newTree;
    }
}
