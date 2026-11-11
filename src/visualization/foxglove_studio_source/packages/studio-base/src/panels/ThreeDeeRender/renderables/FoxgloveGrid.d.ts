import * as THREE from "three";
import { Grid } from "@foxglove/schemas";
import { SettingsTreeAction } from "@foxglove/studio";
import type { RosValue } from "@foxglove/studio-base/players/types";
import { ColorModeSettings } from "./colorMode";
import type { AnyRendererSubscription, IRenderer } from "../IRenderer";
import { BaseUserData, Renderable } from "../Renderable";
import { SceneExtension } from "../SceneExtension";
import { SettingsTreeEntry } from "../SettingsManager";
import { BaseSettings } from "../settings";
type GridColorModeSettings = ColorModeSettings & {
    colorMode: Exclude<ColorModeSettings["colorMode"], "rgb" | "rgba">;
};
export type LayerSettingsFoxgloveGrid = BaseSettings & GridColorModeSettings & {
    frameLocked: boolean;
};
declare const COLOR_MODE_TO_GLSL: {
    [K in GridColorModeSettings["colorMode"] as `COLOR_MODE_${K extends "rgba-fields" ? "RGBA" : Uppercase<K>}`]: number;
};
declare const COLOR_MAP_TO_GLSL: {
    [K in ColorModeSettings["colorMap"] as `COLOR_MAP_${Uppercase<K>}`]: number;
};
interface GridShaderMaterial extends THREE.ShaderMaterial {
    uniforms: {
        map: THREE.IUniform<THREE.DataTexture>;
        colorMode: THREE.IUniform<number>;
        minValue: THREE.IUniform<number>;
        maxValue: THREE.IUniform<number>;
        colorMap: THREE.IUniform<number>;
        colorMapOpacity: THREE.IUniform<number>;
        minGradientColorLinear: THREE.IUniform<THREE.Vector4>;
        maxGradientColorLinear: THREE.IUniform<THREE.Vector4>;
    };
    defines: typeof COLOR_MODE_TO_GLSL & typeof COLOR_MAP_TO_GLSL & {
        PICKING: number;
    };
}
export type FoxgloveGridUserData = BaseUserData & {
    settings: LayerSettingsFoxgloveGrid;
    topic: string;
    foxgloveGrid: Grid;
    mesh: THREE.Mesh;
    texture: THREE.DataTexture;
    material: GridShaderMaterial;
    pickingMaterial: THREE.ShaderMaterial;
};
export declare class FoxgloveGridRenderable extends Renderable<FoxgloveGridUserData> {
    #private;
    dispose(): void;
    details(): Record<string, RosValue>;
    syncPickingMaterial(): void;
    updateMaterial(settings: LayerSettingsFoxgloveGrid): void;
    updateUniforms(foxgloveGrid: Grid, settings: LayerSettingsFoxgloveGrid): void;
    updateTexture(foxgloveGrid: Grid, settings: LayerSettingsFoxgloveGrid): void;
}
export declare class FoxgloveGrid extends SceneExtension<FoxgloveGridRenderable> {
    #private;
    static extensionId: string;
    constructor(renderer: IRenderer, name?: string);
    getSubscriptions(): readonly AnyRendererSubscription[];
    settingsNodes(): SettingsTreeEntry[];
    handleSettingsAction: (action: SettingsTreeAction) => void;
}
export {};
