import * as THREE from "three";
import { PointCloud } from "@foxglove/schemas";
import { SettingsTreeAction } from "@foxglove/studio";
import { LayerSettingsPointExtension } from "@foxglove/studio-base/panels/ThreeDeeRender/renderables/pointExtensionUtils";
import type { RosObject, RosValue } from "@foxglove/studio-base/players/types";
import type { AnyRendererSubscription, IRenderer } from "../IRenderer";
import { BaseUserData, Renderable } from "../Renderable";
import { SceneExtension } from "../SceneExtension";
import { SettingsTreeEntry } from "../SettingsManager";
import { PointCloud2 } from "../ros";
type LayerSettingsPointClouds = LayerSettingsPointExtension & {
    stixelsEnabled: boolean;
    colorFieldComputed: "distance" | undefined;
};
type PointCloudHistoryUserData = BaseUserData & {
    settings: LayerSettingsPointClouds;
    topic: string;
    latestPointCloud: PointCloud | PointCloud2;
    latestOriginalMessage: Record<string, RosValue> | undefined;
    material: THREE.PointsMaterial;
    pickingMaterial: THREE.ShaderMaterial;
    instancePickingMaterial: THREE.ShaderMaterial;
    stixelMaterial: THREE.LineBasicMaterial;
};
export declare class PointCloudHistoryRenderable extends Renderable<PointCloudHistoryUserData> {
    #private;
    pickable: boolean;
    constructor(topic: string, renderer: IRenderer, userData: PointCloudHistoryUserData);
    dispose(): void;
    updatePointCloud(this: PointCloudHistoryRenderable, pointCloud: PointCloud | PointCloud2, originalMessage: RosObject | undefined, settings: LayerSettingsPointClouds, receiveTime: bigint): void;
    startFrame(currentTime: bigint, renderFrameId: string, fixedFrameId: string): void;
    pushHistory(this: PointCloudHistoryRenderable, pointCloud: PointCloud | PointCloud2, originalMessage: RosObject | undefined, settings: LayerSettingsPointClouds, receiveTime: bigint): void;
}
export declare class PointClouds extends SceneExtension<PointCloudHistoryRenderable> {
    #private;
    static extensionId: string;
    constructor(renderer: IRenderer, name?: string);
    getSubscriptions(): readonly AnyRendererSubscription[];
    settingsNodes(): SettingsTreeEntry[];
    startFrame(currentTime: bigint, renderFrameId: string, fixedFrameId: string): void;
    handleSettingsAction: (action: SettingsTreeAction) => void;
}
export declare function createStixelMaterial(settings: LayerSettingsPointClouds): THREE.LineBasicMaterial;
export {};
