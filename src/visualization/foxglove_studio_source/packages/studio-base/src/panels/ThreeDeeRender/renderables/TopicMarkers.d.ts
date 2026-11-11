import { RenderableMarker } from "./markers/RenderableMarker";
import type { IRenderer } from "../IRenderer";
import { BaseUserData, Renderable } from "../Renderable";
import { Marker } from "../ros";
import { BaseSettings } from "../settings";
export type LayerSettingsMarker = BaseSettings & {
    color: string | undefined;
    showOutlines: boolean | undefined;
    selectedIdVariable: string | undefined;
    namespaces: Record<string, LayerSettingsMarkerNamespace>;
};
export type LayerSettingsMarkerNamespace = BaseSettings;
export type MarkerTopicUserData = BaseUserData & {
    topic: string;
    settings: LayerSettingsMarker;
};
export declare class MarkersNamespace {
    namespace: string;
    markersById: Map<number, RenderableMarker>;
    settings: LayerSettingsMarkerNamespace;
    constructor(topic: string, namespace: string, renderer: IRenderer);
}
export declare class TopicMarkers extends Renderable<MarkerTopicUserData> {
    #private;
    pickable: boolean;
    namespaces: Map<string, MarkersNamespace>;
    dispose(): void;
    addMarkerMessage(marker: Marker, receiveTime: bigint): void;
    update(): void;
    startFrame(currentTime: bigint, renderFrameId: string, fixedFrameId: string): void;
}
