import * as THREE from "three";
import { Writable } from "ts-essentials";
import { Immutable, SettingsTreeAction, Topic } from "@foxglove/studio";
import { PanelContextMenuItem } from "@foxglove/studio-base/components/PanelContextMenu";
import { DraggedMessagePath } from "@foxglove/studio-base/components/PanelExtensionAdapter";
import { ImageRenderable, ImageUserData } from "@foxglove/studio-base/panels/ThreeDeeRender/renderables/Images/ImageRenderable";
import { IMessageHandler } from "./MessageHandler";
import type { AnyRendererSubscription, IRenderer, ImageModeConfig, RendererConfig } from "../../IRenderer";
import { SceneExtension } from "../../SceneExtension";
import { SettingsTreeEntry } from "../../SettingsManager";
import { ICameraHandler } from "../ICameraHandler";
interface ImageModeEventMap extends THREE.Object3DEventMap {
    hasModifiedViewChanged: object;
}
export declare const ALL_SUPPORTED_IMAGE_SCHEMAS: Set<string>;
declare const DEFAULT_CONFIG: {
    gradient: [string, string];
    colorMode: "flat" | "rgb" | "rgba" | "gradient" | "colormap" | "rgba-fields";
    flatColor: string;
    colorMap: "turbo" | "rainbow";
    explicitAlpha: number;
    synchronize: boolean;
    flipHorizontal: boolean;
    flipVertical: boolean;
    rotation: 0 | 180 | 90 | 270;
};
type ConfigWithDefaults = ImageModeConfig & typeof DEFAULT_CONFIG;
export declare class ImageMode extends SceneExtension<ImageRenderable, ImageModeEventMap> implements ICameraHandler {
    #private;
    static extensionId: string;
    protected imageRenderable: ImageRenderable | undefined;
    protected readonly messageHandler: IMessageHandler;
    protected readonly supportedImageSchemas: Set<string>;
    constructor(renderer: IRenderer, name?: string);
    protected initMessageHandler(config: Immutable<ConfigWithDefaults>): IMessageHandler;
    hasModifiedView(): boolean;
    resetViewModifications(): void;
    getSubscriptions(): readonly AnyRendererSubscription[];
    dispose(): void;
    removeAllRenderables(): void;
    /** Sets specified image topic on the config and updates calibration topic if a match is found.
     *  Does not check that image topic is different
     **/
    protected setImageTopic(imageTopic: Topic): void;
    settingsNodes(): SettingsTreeEntry[];
    handleSettingsAction: (action: SettingsTreeAction) => void;
    getDropEffectForPath: (path: DraggedMessagePath) => "add" | "replace" | undefined;
    updateConfigForDropPath: (draft: Writable<RendererConfig>, path: DraggedMessagePath) => void;
    protected imageShouldSubscribe: (topic: string) => boolean;
    protected initRenderable(topicName: string, userData: ImageUserData): ImageRenderable;
    protected getImageModeSettings(): Immutable<ConfigWithDefaults>;
    getActiveCamera(): THREE.PerspectiveCamera | THREE.OrthographicCamera;
    handleResize(width: number, height: number, _pixelRatio: number): void;
    setCameraState(): void;
    getCameraState(): undefined;
    getContextMenuItems(): PanelContextMenuItem[];
}
export {};
