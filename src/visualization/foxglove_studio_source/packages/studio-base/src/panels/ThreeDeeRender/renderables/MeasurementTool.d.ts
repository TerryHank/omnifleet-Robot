import * as THREE from "three";
import type { IRenderer } from "../IRenderer";
import { Renderable } from "../Renderable";
import { SceneExtension } from "../SceneExtension";
type MeasurementState = "idle" | "place-first-point" | "place-second-point";
interface MeasurementToolEventMap extends THREE.Object3DEventMap {
    "foxglove.measure-start": object;
    "foxglove.measure-end": object;
}
export declare class MeasurementTool extends SceneExtension<Renderable, MeasurementToolEventMap> {
    #private;
    static extensionId: string;
    state: MeasurementState;
    constructor(renderer: IRenderer, name?: string);
    dispose(): void;
    startMeasuring(): void;
    stopMeasuring(): void;
    startFrame(currentTime: bigint, renderFrameId: string, fixedFrameId: string): void;
}
export {};
