import * as THREE from "three";
import { LineMaterialWithAlphaVertex } from "../../LineMaterialWithAlphaVertex";
import { ColorRGBA, Marker } from "../../ros";
export type LineOptions = {
    resolution: THREE.Vector2;
    worldUnits?: boolean;
};
export declare function markerHasTransparency(marker: Marker): boolean;
export declare function makeStandardMaterial(color: ColorRGBA): THREE.MeshStandardMaterial;
export declare function makeStandardVertexColorMaterial(marker: Marker): THREE.MeshStandardMaterial;
export declare function makeStandardInstancedMaterial(marker: Marker): THREE.MeshStandardMaterial;
export declare function makeLinePrepassMaterial(marker: Marker, options: LineOptions): LineMaterialWithAlphaVertex;
export declare function makeLineMaterial(marker: Marker, options: LineOptions): LineMaterialWithAlphaVertex;
export declare function makeLinePickingMaterial(lineWidth: number, options: LineOptions): THREE.ShaderMaterial;
export declare function makePointsMaterial(marker: Marker): THREE.PointsMaterial;
