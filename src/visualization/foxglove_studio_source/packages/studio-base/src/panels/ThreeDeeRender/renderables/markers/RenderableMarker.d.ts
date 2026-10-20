import * as THREE from "three";
import { RosValue } from "@foxglove/studio-base/players/types";
import type { IRenderer } from "../../IRenderer";
import { BaseUserData, Renderable } from "../../Renderable";
import { Marker } from "../../ros";
import type { LayerSettingsMarker } from "../TopicMarkers";
export type MarkerUserData = BaseUserData & {
    topic: string;
    marker: Marker;
    originalMarker: Marker;
    expiresIn: bigint | undefined;
};
export declare function getMarkerId(topic: string, ns: string, id: number): string;
export declare class RenderableMarker extends Renderable<MarkerUserData> {
    #private;
    constructor(topic: string, marker: Marker, receiveTime: bigint | undefined, renderer: IRenderer);
    idFromMessage(): number | string | undefined;
    selectedIdVariable(): string | undefined;
    getSettings(): LayerSettingsMarker | undefined;
    details(): Record<string, RosValue>;
    update(marker: Marker, receiveTime: bigint | undefined): void;
    protected _markerColorsToLinear(marker: Marker, pointsLength: number, callback: (color: THREE.Vector4Tuple, i: number) => void): void;
}
