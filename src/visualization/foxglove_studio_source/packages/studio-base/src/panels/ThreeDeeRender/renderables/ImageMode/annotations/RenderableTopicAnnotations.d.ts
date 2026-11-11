import * as THREE from "three";
import { PinholeCameraModel } from "@foxglove/den/image";
import { RosObject } from "@foxglove/studio-base/players/types";
import { LabelPool } from "@foxglove/three-text";
import { Annotation as NormalizedAnnotation } from "./types";
/**
 * Holds renderables for all the 2D image annotations on a single topic.
 */
export declare class RenderableTopicAnnotations extends THREE.Object3D {
    #private;
    constructor(topicName: string, labelPool: LabelPool);
    dispose(): void;
    setScale(scale: number, canvasWidth: number, canvasHeight: number, pixelRatio: number): void;
    setOriginalMessage(originalMessage: RosObject | undefined): void;
    setCameraModel(cameraModel: PinholeCameraModel | undefined): void;
    setAnnotations(annotations: NormalizedAnnotation[]): void;
    update(): void;
}
