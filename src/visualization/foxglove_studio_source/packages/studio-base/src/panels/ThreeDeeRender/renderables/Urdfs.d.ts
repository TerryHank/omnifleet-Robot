import type { AnyRendererSubscription, IRenderer } from "../IRenderer";
import { BaseUserData, Renderable } from "../Renderable";
import { SceneExtension } from "../SceneExtension";
import { SettingsTreeEntry } from "../SettingsManager";
import { BaseSettings, CustomLayerSettings } from "../settings";
export type LayerSettingsUrdf = BaseSettings & {
    instanceId: string;
    displayMode: "auto" | "visual" | "collision";
    label: string;
    fallbackColor?: string;
};
export type LayerSettingsCustomUrdf = CustomLayerSettings & {
    layerId: "foxglove.Urdf";
    sourceType: "url" | "filePath" | "param" | "topic";
    url?: string;
    filePath?: string;
    parameter?: string;
    topic?: string;
    framePrefix: string;
    displayMode: "auto" | "visual" | "collision";
    fallbackColor?: string;
};
export type UrdfUserData = BaseUserData & {
    settings: LayerSettingsUrdf | LayerSettingsCustomUrdf;
    fetching?: {
        url: string;
        control: AbortController;
    };
    urdf: string | undefined;
    sourceType: LayerSettingsCustomUrdf["sourceType"] | undefined;
    parameter: string | undefined;
    renderables: Map<string, Renderable>;
};
export declare class UrdfRenderable extends Renderable<UrdfUserData> {
    dispose(): void;
    removeChildren(): void;
}
export declare class Urdfs extends SceneExtension<UrdfRenderable> {
    #private;
    static extensionId: string;
    constructor(renderer: IRenderer, name?: string);
    getSubscriptions(): readonly AnyRendererSubscription[];
    settingsNodes(): SettingsTreeEntry[];
    removeAllRenderables(): void;
    startFrame(currentTime: bigint, renderFrameId: string, fixedFrameId: string): void;
}
