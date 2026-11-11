import * as THREE from "three";
import { LoadedModel } from "../ModelCache";
export type GltfMesh = THREE.Mesh<THREE.BufferGeometry, THREE.MeshStandardMaterial | THREE.MeshStandardMaterial[]>;
export declare function removeLights(model: LoadedModel): void;
export declare function replaceMaterials(model: LoadedModel, material: THREE.MeshStandardMaterial): void;
