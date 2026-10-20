import * as THREE from "three";
import { SettingsTreeAction } from "@foxglove/studio";
import type { RosValue } from "@foxglove/studio-base/players/types";
import type { AnyRendererSubscription, IRenderer } from "../IRenderer";
import { BaseUserData, Renderable } from "../Renderable";
import { SceneExtension } from "../SceneExtension";
import { SettingsTreeEntry } from "../SettingsManager";
import { OccupancyGrid } from "../ros";
import { BaseSettings } from "../settings";
type ColorModes = "custom" | "costmap" | "map" | "raw";
export type LayerSettingsOccupancyGrid = BaseSettings & {
    frameLocked: boolean;
    minColor: string;
    maxColor: string;
    unknownColor: string;
    invalidColor: string;
    colorMode: ColorModes;
    alpha: number;
};
export type OccupancyGridUserData = BaseUserData & {
    settings: LayerSettingsOccupancyGrid;
    topic: string;
    occupancyGrid: OccupancyGrid;
    mesh: THREE.Mesh;
    texture: THREE.DataTexture;
    material: THREE.MeshBasicMaterial;
    pickingMaterial: THREE.ShaderMaterial;
};
export declare class OccupancyGridRenderable extends Renderable<OccupancyGridUserData> {
    dispose(): void;
    details(): Record<string, RosValue>;
}
export declare class OccupancyGrids extends SceneExtension<OccupancyGridRenderable> {
    #private;
    static extensionId: string;
    constructor(renderer: IRenderer, name?: string);
    getSubscriptions(): readonly AnyRendererSubscription[];
    settingsNodes(): SettingsTreeEntry[];
    handleSettingsAction: (action: SettingsTreeAction) => void;
}
export {};
