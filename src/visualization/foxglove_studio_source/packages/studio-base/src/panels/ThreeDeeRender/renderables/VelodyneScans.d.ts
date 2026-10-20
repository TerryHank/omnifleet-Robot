import { SettingsTreeAction } from "@foxglove/studio";
import { PointCloudHistoryRenderable } from "@foxglove/studio-base/panels/ThreeDeeRender/renderables/PointClouds";
import type { AnyRendererSubscription, IRenderer } from "../IRenderer";
import { SceneExtension } from "../SceneExtension";
import { SettingsTreeEntry } from "../SettingsManager";
export declare class VelodyneScans extends SceneExtension<PointCloudHistoryRenderable> {
    #private;
    static extensionId: string;
    constructor(renderer: IRenderer, name?: string);
    getSubscriptions(): readonly AnyRendererSubscription[];
    settingsNodes(): SettingsTreeEntry[];
    handleSettingsAction: (action: SettingsTreeAction) => void;
    startFrame(currentTime: bigint, renderFrameId: string, fixedFrameId: string): void;
}
