import * as THREE from "three";
import { PinholeCameraModel } from "@foxglove/den/image";
import { Immutable, Topic } from "@foxglove/studio";
import { Path } from "@foxglove/studio-base/panels/ThreeDeeRender/LayerErrors";
import { LabelPool } from "@foxglove/three-text";
import { AnyRendererSubscription, ImageModeConfig } from "../../../IRenderer";
import { SettingsTreeEntry } from "../../../SettingsManager";
import { IMessageHandler } from "../MessageHandler";
interface ImageAnnotationsContext {
    initialScale: number;
    initialCanvasWidth: number;
    initialCanvasHeight: number;
    initialPixelRatio: number;
    topics(): readonly Topic[];
    config(): Immutable<ImageModeConfig>;
    updateConfig(updateHandler: (draft: ImageModeConfig) => void): void;
    updateSettingsTree(): void;
    labelPool: LabelPool;
    messageHandler: IMessageHandler;
    addSettingsError(path: Path, errorId: string, errorMessage: string): void;
    removeSettingsError(path: Path, errorId: string): void;
}
/**
 * This class handles settings and rendering for ImageAnnotations/ImageMarkers.
 */
export declare class ImageAnnotations extends THREE.Object3D {
    #private;
    supportedAnnotationSchemas: Set<string>;
    constructor(context: ImageAnnotationsContext);
    getSubscriptions(): readonly AnyRendererSubscription[];
    handleTopicsChanged(topics: readonly Topic[] | undefined): void;
    dispose(): void;
    /** Called when seeking or a new data source is loaded.  */
    removeAllRenderables(): void;
    updateScale(scale: number, canvasWidth: number, canvasHeight: number, pixelRatio: number): void;
    updateCameraModel(cameraModel: PinholeCameraModel): void;
    settingsNodes(): SettingsTreeEntry[];
}
export {};
