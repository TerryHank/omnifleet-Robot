import * as THREE from "three";
import { RenderableMarker } from "./RenderableMarker";
import type { IRenderer } from "../../IRenderer";
import { Marker } from "../../ros";
export declare class RenderableArrow extends RenderableMarker {
    #private;
    shaftMesh: THREE.Mesh<THREE.CylinderGeometry, THREE.MeshStandardMaterial>;
    headMesh: THREE.Mesh<THREE.ConeGeometry, THREE.MeshStandardMaterial>;
    constructor(topic: string, marker: Marker, receiveTime: bigint | undefined, renderer: IRenderer);
    dispose(): void;
    update(newMarker: Marker, receiveTime: bigint | undefined): void;
}
