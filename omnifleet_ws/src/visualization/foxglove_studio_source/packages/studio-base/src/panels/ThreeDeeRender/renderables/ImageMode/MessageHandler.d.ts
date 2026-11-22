import { CompressedImage, RawImage, ImageAnnotations as FoxgloveImageAnnotations } from "@foxglove/schemas";
import { Immutable, MessageEvent } from "@foxglove/studio";
import { HUDItem, HUDItemManager } from "@foxglove/studio-base/panels/ThreeDeeRender/HUDItemManager";
import { ImageModeConfig } from "@foxglove/studio-base/panels/ThreeDeeRender/IRenderer";
import { AnyImage } from "@foxglove/studio-base/panels/ThreeDeeRender/renderables/Images/ImageTypes";
import { ImageMarker as RosImageMarker, ImageMarkerArray as RosImageMarkerArray } from "@foxglove/studio-base/types/Messages";
import { Annotation } from "./annotations/types";
import { PartialMessageEvent } from "../../SceneExtension";
import { CompressedImage as RosCompressedImage, Image as RosImage, CameraInfo } from "../../ros";
type NormalizedAnnotations = {
    originalMessage: MessageEvent<RosImageMarkerArray | RosImageMarker | FoxgloveImageAnnotations>;
    annotations: Annotation[];
};
type Config = Pick<ImageModeConfig, "synchronize" | "annotations" | "calibrationTopic" | "imageTopic">;
type MessageHandlerState = {
    image?: MessageEvent<AnyImage>;
    cameraInfo?: CameraInfo;
    annotationsByTopic: Map<string, NormalizedAnnotations>;
    /** Topics that were present in a potential synchronized set */
    presentAnnotationTopics?: string[];
    /** Topics that were missing so that a synchronized set could not be found */
    missingAnnotationTopics?: string[];
};
export type MessageRenderState = Readonly<Partial<MessageHandlerState>>;
type RenderStateListener = (newState: MessageRenderState, oldState: MessageRenderState | undefined) => void;
export declare const WAITING_FOR_BOTH_HUD_ITEM: HUDItem;
export declare const WAITING_FOR_CALIBRATION_HUD_ITEM: HUDItem;
export declare const WAITING_FOR_IMAGE_NOTICE_HUD_ITEM: HUDItem;
export declare const WAITING_FOR_IMAGE_EMPTY_HUD_ITEM: HUDItem;
export declare const WAITING_FOR_SYNC_NOTICE_HUD_ITEM: HUDItem;
export declare const WAITING_FOR_SYNC_EMPTY_HUD_ITEM: HUDItem;
/**
 * Processes and normalizes incoming messages and manages state of
 * messages to be rendered given the ImageMode config. A large part of this responsibility
 * is managing state in synchronized mode and ensuring that the a synchronized set of image and
 * annotations are handed off to the SceneExtension for rendering.
 */
export declare class MessageHandler implements IMessageHandler {
    #private;
    /**
     *
     * @param config - subset of ImageMode settings required for message handling
     */
    constructor(config: Immutable<Config>, hud: HUDItemManager);
    addListener(listener: RenderStateListener): void;
    removeListener(listener: RenderStateListener): void;
    handleRosRawImage: (messageEvent: PartialMessageEvent<RosImage>) => void;
    handleRosCompressedImage: (messageEvent: PartialMessageEvent<RosCompressedImage>) => void;
    handleRawImage: (messageEvent: PartialMessageEvent<RawImage>) => void;
    handleCompressedImage: (messageEvent: PartialMessageEvent<CompressedImage>) => void;
    protected handleImage(message: PartialMessageEvent<AnyImage>, image: AnyImage): void;
    handleCameraInfo: (message: PartialMessageEvent<CameraInfo>) => void;
    handleAnnotations: (messageEvent: MessageEvent<FoxgloveImageAnnotations | RosImageMarker | RosImageMarkerArray>) => void;
    setConfig(newConfig: Immutable<ImageModeConfig>): void;
    setAvailableAnnotationTopics(topicNames: string[]): void;
    clear(): void;
    /** Do not use. only public for testing */
    getRenderStateAndUpdateHUD(): Readonly<Partial<MessageHandlerState>>;
}
export interface IMessageHandler {
    handleRosRawImage: (messageEvent: PartialMessageEvent<RosImage>) => void;
    handleRosCompressedImage: (messageEvent: PartialMessageEvent<RosCompressedImage>) => void;
    handleRawImage: (messageEvent: PartialMessageEvent<RawImage>) => void;
    handleCompressedImage: (messageEvent: PartialMessageEvent<CompressedImage>) => void;
    handleCameraInfo: (message: PartialMessageEvent<CameraInfo>) => void;
    handleAnnotations: (messageEvent: MessageEvent<FoxgloveImageAnnotations | RosImageMarker | RosImageMarkerArray>) => void;
    /**
     *  Add listener that will trigger every time the state changes
     *  The listener will be called with the new state and the previous state.
     */
    addListener(listener: RenderStateListener): void;
    /** Remove listener from being called on state update */
    removeListener(listener: RenderStateListener): void;
    setConfig(newConfig: Immutable<Partial<ImageModeConfig>>): void;
    clear(): void;
    getRenderStateAndUpdateHUD(): Readonly<Partial<MessageHandlerState>>;
    /**
     * Set what topics are available on the current source.
     * This will prevent having to wait on annotations that are in the layout but not in the source.
     */
    setAvailableAnnotationTopics(availableAnnotations: string[]): void;
}
export {};
