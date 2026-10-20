import * as THREE from "three";
import { BuiltinPanelExtensionContext } from "@foxglove/studio-base/components/PanelExtensionAdapter";
export type MeshUpAxis = "y_up" | "z_up";
export declare const DEFAULT_MESH_UP_AXIS: MeshUpAxis;
export type ModelCacheOptions = {
    edgeMaterial: THREE.Material;
    ignoreColladaUpAxis: boolean;
    meshUpAxis: MeshUpAxis;
    fetchAsset: BuiltinPanelExtensionContext["unstable_fetchAsset"];
};
type LoadModelOptions = {
    overrideMediaType?: string;
    /** A URL to e.g. a URDf which may be used to resolve mesh package:// URLs */
    referenceUrl?: string;
};
export type LoadedModel = THREE.Group | THREE.Scene;
type ErrorCallback = (err: Error) => void;
export declare class ModelCache {
    #private;
    readonly options: ModelCacheOptions;
    constructor(options: ModelCacheOptions);
    load(url: string, opts: LoadModelOptions, reportError: ErrorCallback): Promise<LoadedModel | undefined>;
    dispose(): void;
}
export declare const EDGE_LINE_SEGMENTS_NAME = "edges";
export {};
