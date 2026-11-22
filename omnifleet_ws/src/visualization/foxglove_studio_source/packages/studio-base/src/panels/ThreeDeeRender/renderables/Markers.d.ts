import { SettingsTreeAction } from "@foxglove/studio";
import { TopicMarkers } from "./TopicMarkers";
import type { AnyRendererSubscription, IRenderer } from "../IRenderer";
import { SceneExtension } from "../SceneExtension";
import { SettingsTreeEntry } from "../SettingsManager";
import { Marker } from "../ros";
export declare class Markers extends SceneExtension<TopicMarkers> {
    #private;
    static extensionId: string;
    constructor(renderer: IRenderer, name?: string);
    getSubscriptions(): readonly AnyRendererSubscription[];
    settingsNodes(): SettingsTreeEntry[];
    startFrame(currentTime: bigint, renderFrameId: string, fixedFrameId: string): void;
    handleSettingsAction: (action: SettingsTreeAction) => void;
    addMarkerArray(topic: string, markerArray: Marker[], receiveTime: bigint): void;
}
