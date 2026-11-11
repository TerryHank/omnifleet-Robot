import * as THREE from "three";
import type { IRenderer } from "../IRenderer";
export declare const AXIS_LENGTH: number;
export declare class Axis extends THREE.Object3D {
    #private;
    constructor(name: string, renderer: IRenderer);
    dispose(): void;
}
