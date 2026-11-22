import * as THREE from "three";
import type { Renderable } from "./Renderable";
export type PickedRenderable = {
    renderable: Renderable;
    instanceIndex?: number;
};
export type PickerOptions = {
    debug?: boolean;
    /**
     * Disable the setting of the projection matrix in the picking pass.
     * Use this if you are setting the projection matrix of the camera manually elsewhere
     */
    disableSetViewOffset?: boolean;
};
/**
 * Handles picking of objects in a scene (detecting 3D objects at a given screen
 * coordinate). This works by performing a second rendering pass after
 * `WebGLRenderer.renderLists` has been populated from a normal rendering pass.
 * In the second pass, objectIds are written as colors to a small offscreen
 * rendering target surrounding the sample point. The color at the sample point
 * is then read back and used to determine which object was picked.
 *
 * Objects can set their own `userData.pickingMaterial` to override the default
 * shader used for picking.
 */
export declare class Picker {
    #private;
    constructor(gl: THREE.WebGLRenderer, scene: THREE.Scene);
    dispose(): void;
    pick(x: number, y: number, camera: THREE.OrthographicCamera | THREE.PerspectiveCamera, options?: PickerOptions): number;
    pickInstance(x: number, y: number, camera: THREE.OrthographicCamera | THREE.PerspectiveCamera, renderable: THREE.Object3D, options?: PickerOptions): number;
}
