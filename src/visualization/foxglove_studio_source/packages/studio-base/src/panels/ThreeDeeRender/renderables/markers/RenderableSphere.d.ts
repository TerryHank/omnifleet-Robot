import * as THREE from "three";
import { RenderableMarker } from "./RenderableMarker";
import type { IRenderer } from "../../IRenderer";
import { DetailLevel } from "../../lod";
import { Marker } from "../../ros";
export declare class RenderableSphere extends RenderableMarker {
    mesh: THREE.Mesh<THREE.SphereGeometry, THREE.MeshStandardMaterial>;
    constructor(topic: string, marker: Marker, receiveTime: bigint | undefined, renderer: IRenderer);
    dispose(): void;
    update(newMarker: Marker, receiveTime: bigint | undefined): void;
}
export declare function createGeometry(lod: DetailLevel): THREE.SphereGeometry;
