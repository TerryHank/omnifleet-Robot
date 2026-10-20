import * as THREE from "three";
import { ColorRGBA, Vector3 } from "./ros";
/**
 * Extends InstancedMesh with a set() method that takes a list of points and
 * colors and dynamically resizes the buffer attributes.
 */
export declare class DynamicInstancedMesh<TGeometry extends THREE.BufferGeometry = THREE.BufferGeometry, TMaterial extends THREE.Material | THREE.Material[] = THREE.Material | THREE.Material[]> extends THREE.InstancedMesh<TGeometry, TMaterial> {
    #private;
    constructor(geometry: TGeometry, material: TMaterial, initialCapacity?: number);
    set(points: Vector3[], scale: Vector3, colors: ColorRGBA[], defaultColor: ColorRGBA): void;
}
