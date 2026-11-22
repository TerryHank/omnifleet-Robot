import { SettingsTreeAction } from "@foxglove/studio";
import type { RosValue } from "@foxglove/studio-base/players/types";
import { Axis } from "./Axis";
import { RenderableArrow } from "./markers/RenderableArrow";
import { RenderableSphere } from "./markers/RenderableSphere";
import type { AnyRendererSubscription, IRenderer } from "../IRenderer";
import { BaseUserData, Renderable } from "../Renderable";
import { SceneExtension } from "../SceneExtension";
import { SettingsTreeEntry } from "../SettingsManager";
import { Marker, PoseWithCovarianceStamped, PoseStamped, ColorRGBA } from "../ros";
import { BaseSettings } from "../settings";
type DisplayType = "axis" | "arrow";
export type LayerSettingsPose = BaseSettings & {
    type: DisplayType;
    axisScale: number;
    arrowScale: [number, number, number];
    color: string;
    showCovariance: boolean;
    covarianceColor: string;
};
export type PoseUserData = BaseUserData & {
    settings: LayerSettingsPose;
    topic: string;
    poseMessage: PoseStamped | PoseWithCovarianceStamped;
    originalMessage: Record<string, RosValue>;
    axis?: Axis;
    arrow?: RenderableArrow;
    sphere?: RenderableSphere;
};
export declare class PoseRenderable extends Renderable<PoseUserData> {
    dispose(): void;
    details(): Record<string, RosValue>;
}
export declare class Poses extends SceneExtension<PoseRenderable> {
    #private;
    static extensionId: string;
    constructor(renderer: IRenderer, name?: string);
    getSubscriptions(): readonly AnyRendererSubscription[];
    settingsNodes(): SettingsTreeEntry[];
    handleSettingsAction: (action: SettingsTreeAction) => void;
}
export declare function createArrowMarker(arrowScale: [number, number, number], color: ColorRGBA): Marker;
export {};
