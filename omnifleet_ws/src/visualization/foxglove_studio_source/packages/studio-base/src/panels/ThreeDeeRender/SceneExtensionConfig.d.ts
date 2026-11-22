import { ImageMode } from "@foxglove/studio-base/panels/ThreeDeeRender/renderables/ImageMode/ImageMode";
import { IRenderer } from "./IRenderer";
import { SceneExtension } from "./SceneExtension";
import { MeasurementTool } from "./renderables/MeasurementTool";
import { PublishClickTool } from "./renderables/PublishClickTool";
import { InterfaceMode } from "./types";
export type SceneExtensionConfig = {
    /** Reserved because the Renderer has members that reference them specifically */
    reserved: ReservedSceneExtensionConfig;
    extensionsById: Record<string, ExtensionOverride<SceneExtension>>;
};
export type ReservedSceneExtensionConfig = {
    imageMode: ExtensionOverride<ImageMode>;
    measurementTool: ExtensionOverride<MeasurementTool>;
    publishClickTool: ExtensionOverride<PublishClickTool>;
};
export type ExtensionOverride<ExtensionType extends SceneExtension> = {
    init: (renderer: IRenderer) => ExtensionType;
    /** Which interfaceModes this extension is supported in. If undefined, will default be present in BOTH '3d' and 'image' modes */
    supportedInterfaceModes?: InterfaceMode[];
};
export declare const DEFAULT_SCENE_EXTENSION_CONFIG: SceneExtensionConfig;
