import { SettingsTreeAction } from "@foxglove/studio";
import { RenderableLineList } from "./markers/RenderableLineList";
import type { IRenderer } from "../IRenderer";
import { BaseUserData, Renderable } from "../Renderable";
import { SceneExtension } from "../SceneExtension";
import { SettingsTreeEntry } from "../SettingsManager";
import { CustomLayerSettings } from "../settings";
export type LayerSettingsGrid = CustomLayerSettings & {
    layerId: "foxglove.Grid";
    frameId: string | undefined;
    size: number;
    divisions: number;
    lineWidth: number;
    color: string;
    position: [number, number, number];
    rotation: [number, number, number];
};
export type GridUserData = BaseUserData & {
    settings: LayerSettingsGrid;
    lineList: RenderableLineList;
};
export declare class GridRenderable extends Renderable<GridUserData> {
    dispose(): void;
}
export declare class Grids extends SceneExtension<GridRenderable> {
    #private;
    static extensionId: string;
    constructor(renderer: IRenderer, name?: string);
    dispose(): void;
    removeAllRenderables(): void;
    settingsNodes(): SettingsTreeEntry[];
    startFrame(currentTime: bigint, renderFrameId: string, fixedFrameId: string): void;
    handleSettingsAction: (action: SettingsTreeAction) => void;
}
