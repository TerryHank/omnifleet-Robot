import { SettingsTreeAction } from "@foxglove/studio";
import type { RosValue } from "@foxglove/studio-base/players/types";
import { Axis } from "./Axis";
import { RenderableArrow } from "./markers/RenderableArrow";
import { RenderableLineStrip } from "./markers/RenderableLineStrip";
import type { AnyRendererSubscription, IRenderer } from "../IRenderer";
import { BaseUserData, Renderable } from "../Renderable";
import { SceneExtension } from "../SceneExtension";
import { SettingsTreeEntry } from "../SettingsManager";
import { PoseArray } from "../ros";
import { BaseSettings } from "../settings";
type Gradient = [string, string];
type DisplayType = "axis" | "arrow" | "line";
export type LayerSettingsPoseArray = BaseSettings & {
    type: DisplayType;
    axisScale: number;
    arrowScale: [number, number, number];
    lineWidth: number;
    gradient: Gradient;
};
export type PoseArrayUserData = BaseUserData & {
    settings: LayerSettingsPoseArray;
    topic: string;
    poseArrayMessage: PoseArray;
    originalMessage: Record<string, RosValue>;
    axes: Axis[];
    arrows: RenderableArrow[];
    lineStrip?: RenderableLineStrip;
};
export declare class PoseArrayRenderable extends Renderable<PoseArrayUserData> {
    dispose(): void;
    details(): Record<string, RosValue>;
    removeArrows(): void;
    removeAxes(): void;
    removeLineStrip(): void;
}
export declare class PoseArrays extends SceneExtension<PoseArrayRenderable> {
    #private;
    static extensionId: string;
    constructor(renderer: IRenderer, name?: string);
    getSubscriptions(): readonly AnyRendererSubscription[];
    settingsNodes(): SettingsTreeEntry[];
    handleSettingsAction: (action: SettingsTreeAction) => void;
}
export {};
