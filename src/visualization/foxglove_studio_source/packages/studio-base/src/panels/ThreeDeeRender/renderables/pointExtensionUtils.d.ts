import * as THREE from "three";
import { SettingsTreeNode, Topic } from "@foxglove/studio";
import { DynamicBufferGeometry } from "@foxglove/studio-base/panels/ThreeDeeRender/DynamicBufferGeometry";
import { IRenderer } from "@foxglove/studio-base/panels/ThreeDeeRender/IRenderer";
import { BaseUserData, Renderable } from "@foxglove/studio-base/panels/ThreeDeeRender/Renderable";
import { BaseSettings } from "@foxglove/studio-base/panels/ThreeDeeRender/settings";
import { LaserScanMaterial } from "./LaserScans";
import { ColorModeSettings } from "./colorMode";
export type LayerSettingsPointExtension = BaseSettings & ColorModeSettings & {
    pointSize: number;
    pointShape: "circle" | "square";
    decayTime: number;
};
export declare const DEFAULT_POINT_SETTINGS: LayerSettingsPointExtension;
export declare const POINT_CLOUD_REQUIRED_FIELDS: string[];
/**
 * Creates settings node for Point cloud and scan topics
 * @param topic - topic to get settings node for
 * @param messageFields - message fields or required fields for the topic
 * @param config - current topic settings
 * @param defaultSettings - (optional) default settings to use
 * @returns  - settings node for the topic
 */
export declare function pointSettingsNode(topic: Topic, messageFields: string[], config: Partial<LayerSettingsPointExtension>, defaultSettings?: LayerSettingsPointExtension): SettingsTreeNode;
/**
 * Creates a THREE.Points object for a point cloud and scan messages
 * @param topic - topic name string for naming geometry
 * @param usage - THREE draw usage (ex: THREE.StaticDrawUsage)
 * @returns
 */
export declare function createGeometry(topic: string, usage: THREE.Usage): DynamicBufferGeometry;
type Material = THREE.PointsMaterial | LaserScanMaterial;
export declare function pointCloudColorEncoding<T extends LayerSettingsPointExtension>(settings: T): "srgb" | "linear";
export declare class PointsRenderable<TUserData extends BaseUserData = BaseUserData> extends Renderable<TUserData, undefined> {
    #private;
    readonly geometry: DynamicBufferGeometry;
    pickableInstances: boolean;
    constructor(name: string, userData: TUserData, geometry: DynamicBufferGeometry, material: Material, pickingMaterial: THREE.Material, instancePickingMaterial: THREE.Material);
    dispose(): void;
    updateMaterial(material: Material): void;
}
export declare function pointCloudMaterial<T extends LayerSettingsPointExtension>(settings: T): THREE.PointsMaterial;
export declare function createPickingMaterial<T extends LayerSettingsPointExtension>(settings: T): THREE.ShaderMaterial;
export declare function createInstancePickingMaterial<T extends LayerSettingsPointExtension>(settings: T): THREE.ShaderMaterial;
type RenderObjectHistoryUserData = BaseUserData & {
    topic: string;
    settings: LayerSettingsPointExtension;
};
type DisposableObject = THREE.Object3D & {
    dispose(): void;
};
type HistoryEntry<TRenderable extends DisposableObject> = {
    receiveTime: bigint;
    messageTime: bigint;
    renderable: TRenderable;
};
/**
 * Class that handles lifecycle of 3d object history over the decay time
 * This class encapsulates the functionality of showing the history of an object within a specified decay time.
 * Meant to be extensible for all kinds of renderables that need to show old points over decay time.
 * See LaserScansRenderable and PointCloudsRenderable for examples.
 */
export declare class RenderObjectHistory<TRenderable extends DisposableObject> {
    #private;
    constructor({ initial, renderer, parentRenderable, }: {
        initial: HistoryEntry<TRenderable>;
        renderer: IRenderer;
        parentRenderable: Renderable<RenderObjectHistoryUserData>;
    });
    addHistoryEntry(entry: HistoryEntry<TRenderable>): void;
    forEach(callback: (entry: HistoryEntry<TRenderable>) => void): void;
    updateHistoryFromCurrentTime(currentTime: bigint): void;
    updatePoses(currentTime: bigint, renderFrameId: string, fixedFrameId: string): void;
    latest(): HistoryEntry<TRenderable>;
    /** Removes all but the last renderable, which would be the current object used in rendering. */
    clearHistory(): void;
    dispose(): void;
}
export {};
