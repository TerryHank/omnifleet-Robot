import * as THREE from "three";
import type { IRenderer } from "../IRenderer";
import { Renderable } from "../Renderable";
import { SceneExtension } from "../SceneExtension";
import { Point, Pose } from "../transforms/geometry";
export type PublishClickType = "pose_estimate" | "pose" | "point";
export type PublishClickState = "idle" | "place-first-point" | "place-second-point";
export interface PublishClickEventMap extends THREE.Object3DEventMap {
    "foxglove.publish-start": object;
    "foxglove.publish-end": object;
    "foxglove.publish-type-change": object;
    "foxglove.publish-submit": {
        publishClickType: "point";
        point: Point;
    } | {
        publishClickType: "pose" | "pose_estimate";
        pose: Pose;
    };
}
export declare class PublishClickTool extends SceneExtension<Renderable, PublishClickEventMap> {
    #private;
    publishClickType: PublishClickType;
    state: PublishClickState;
    constructor(renderer: IRenderer);
    dispose(): void;
    setPublishClickType(type: PublishClickType): void;
    start(): void;
    stop(): void;
}
