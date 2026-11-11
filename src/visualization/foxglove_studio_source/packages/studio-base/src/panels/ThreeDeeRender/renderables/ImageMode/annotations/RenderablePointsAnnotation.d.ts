import { PinholeCameraModel } from "@foxglove/den/image";
import { RosObject, RosValue } from "@foxglove/studio-base/players/types";
import { PointsAnnotation as NormalizedPointsAnnotation } from "./types";
import { BaseUserData, Renderable } from "../../../Renderable";
/**
 * 2D points annotation with style=points (points rendered as dots).
 */
export declare class RenderablePointsAnnotation extends Renderable<BaseUserData, /*TRenderer=*/ undefined> {
    #private;
    constructor(topicName: string);
    dispose(): void;
    details(): Record<string, RosValue>;
    setScale(scale: number, _canvasWidth: number, _canvasHeight: number, pixelRatio: number): void;
    setCameraModel(cameraModel: PinholeCameraModel | undefined): void;
    setAnnotation(annotation: NormalizedPointsAnnotation & {
        style: "points";
    }, originalMessage: RosObject | undefined): void;
    update(): void;
}
