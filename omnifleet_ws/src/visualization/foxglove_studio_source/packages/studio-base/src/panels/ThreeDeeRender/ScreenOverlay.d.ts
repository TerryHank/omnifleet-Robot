import * as THREE from "three";
import type { IRenderer } from "./IRenderer";
export declare class ScreenOverlay extends THREE.Object3D {
    #private;
    constructor(renderer: IRenderer);
    setColor(color: THREE.Color, opacity: number): void;
}
