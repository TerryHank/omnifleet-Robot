import * as THREE from "three";
import { Line2 } from "three/examples/jsm/lines/Line2";
import { SettingsTreeAction } from "@foxglove/studio";
import type { RosValue } from "@foxglove/studio-base/players/types";
import { Label } from "@foxglove/three-text";
import { Axis } from "./Axis";
import type { IRenderer } from "../IRenderer";
import { BaseUserData, Renderable } from "../Renderable";
import { SceneExtension } from "../SceneExtension";
import { SettingsTreeEntry } from "../SettingsManager";
import { BaseSettings } from "../settings";
export type LayerSettingsTransform = BaseSettings & {
    xyzOffset: Readonly<[number | undefined, number | undefined, number | undefined]>;
    rpyCoefficient: Readonly<[number | undefined, number | undefined, number | undefined]>;
};
export type FrameAxisUserData = BaseUserData & {
    axis: Axis;
    label: Label;
    parentLine: Line2;
};
declare class FrameAxisRenderable extends Renderable<FrameAxisUserData> {
    dispose(): void;
    details(): Record<string, RosValue>;
}
export declare class FrameAxes extends SceneExtension<FrameAxisRenderable> {
    #private;
    static extensionId: string;
    constructor(renderer: IRenderer, defaultRenderableSettings: Partial<LayerSettingsTransform>, name?: string);
    dispose(): void;
    removeAllRenderables(): void;
    settingsNodes(): SettingsTreeEntry[];
    startFrame(currentTime: bigint, renderFrameId: string, fixedFrameId: string): void;
    setColorScheme(colorScheme: "dark" | "light", backgroundColor: THREE.Color | undefined): void;
    handleSettingsAction: (action: SettingsTreeAction) => void;
}
export {};
