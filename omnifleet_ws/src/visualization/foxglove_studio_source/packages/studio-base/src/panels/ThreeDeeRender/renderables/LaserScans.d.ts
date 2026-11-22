import * as THREE from "three";
import { Time } from "@foxglove/rostime";
import { SettingsTreeAction } from "@foxglove/studio";
import { LayerSettingsPointExtension } from "@foxglove/studio-base/panels/ThreeDeeRender/renderables/pointExtensionUtils";
import type { RosObject, RosValue } from "@foxglove/studio-base/players/types";
import { AnyRendererSubscription, IRenderer } from "../IRenderer";
import { BaseUserData, Renderable } from "../Renderable";
import { SceneExtension } from "../SceneExtension";
import { SettingsTreeEntry } from "../SettingsManager";
import { Pose } from "../transforms";
type LayerSettingsLaserScan = LayerSettingsPointExtension;
type NormalizedLaserScan = {
    timestamp: Time;
    frame_id: string;
    pose: Pose;
    start_angle: number;
    end_angle: number;
    range_min: number;
    range_max: number;
    ranges: Float32Array;
    intensities: Float32Array;
};
type LaserScanHistoryUserData = BaseUserData & {
    settings: LayerSettingsLaserScan;
    topic: string;
    latestLaserScan: NormalizedLaserScan;
    latestOriginalMessage: Record<string, RosValue> | undefined;
};
declare class LaserScanHistoryRenderable extends Renderable<LaserScanHistoryUserData> {
    #private;
    pickable: boolean;
    constructor(topic: string, renderer: IRenderer, userData: LaserScanHistoryUserData);
    dispose(): void;
    updateLaserScan(laserScan: NormalizedLaserScan, originalMessage: RosObject | undefined, settings: LayerSettingsLaserScan, receiveTime: bigint): void;
    invalidateLastEntry(): void;
    startFrame(currentTime: bigint, renderFrameId: string, fixedFrameId: string): void;
}
export declare class LaserScans extends SceneExtension<LaserScanHistoryRenderable> {
    #private;
    static extensionId: string;
    constructor(renderer: IRenderer, name?: string);
    getSubscriptions(): readonly AnyRendererSubscription[];
    settingsNodes(): SettingsTreeEntry[];
    startFrame(currentTime: bigint, renderFrameId: string, fixedFrameId: string): void;
    handleSettingsAction: (action: SettingsTreeAction) => void;
}
export declare class LaserScanMaterial extends THREE.RawShaderMaterial {
    #private;
    constructor({ picking }?: {
        picking?: boolean;
    });
    updateUniforms(settings: LayerSettingsLaserScan, laserScan: NormalizedLaserScan): void;
    setPixelRatio(pixelRatio: number): void;
}
export {};
