import { PinholeCameraModel } from "@foxglove/den/image";
import { RosObject, RosValue } from "@foxglove/studio-base/players/types";
import { LabelPool } from "@foxglove/three-text";
import { TextAnnotation as NormalizedTextAnnotation } from "./types";
import { BaseUserData, Renderable } from "../../../Renderable";
/**
 * Handles rendering of 2D text annotations.
 */
export declare class RenderableTextAnnotation extends Renderable<BaseUserData, /*TRenderer=*/ undefined> {
    #private;
    constructor(topicName: string, labelPool: LabelPool);
    dispose(): void;
    details(): Record<string, RosValue>;
    setScale(scale: number, _canvasWidth: number, _canvasHeight: number, _pixelRatio: number): void;
    setCameraModel(cameraModel: PinholeCameraModel | undefined): void;
    setAnnotation(annotation: NormalizedTextAnnotation, originalMessage: RosObject | undefined): void;
    update(): void;
}
