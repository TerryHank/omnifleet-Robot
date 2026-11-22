import * as THREE from "three";
import { SettingsTreeAction } from "@foxglove/studio";
import { ICameraHandler } from "@foxglove/studio-base/panels/ThreeDeeRender/renderables/ICameraHandler";
import { AnyFrameId, Pose } from "@foxglove/studio-base/panels/ThreeDeeRender/transforms";
import type { IRenderer } from "../IRenderer";
import { SceneExtension } from "../SceneExtension";
import { SettingsTreeEntry } from "../SettingsManager";
import { CameraState } from "../camera";
export declare class CameraStateSettings extends SceneExtension implements ICameraHandler {
    #private;
    unfollowPoseSnapshot: Pose | undefined;
    constructor(renderer: IRenderer, canvas: HTMLCanvasElement, aspect: number);
    dispose(): void;
    settingsNodes(): SettingsTreeEntry[];
    handleSettingsAction: (action: SettingsTreeAction) => void;
    startFrame(currentTime: bigint, renderFrameId: AnyFrameId, fixedFrameId: AnyFrameId): void;
    getActiveCamera(): THREE.PerspectiveCamera | THREE.OrthographicCamera;
    handleResize(width: number, height: number, _pixelRatio: number): void;
    getCameraState(): CameraState;
    setCameraState(cameraState: CameraState): void;
}
