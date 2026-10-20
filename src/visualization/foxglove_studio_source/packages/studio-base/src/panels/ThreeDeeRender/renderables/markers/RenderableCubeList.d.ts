import { RenderableMarker } from "./RenderableMarker";
import type { Renderer } from "../../Renderer";
import { Marker } from "../../ros";
export declare class RenderableCubeList extends RenderableMarker {
    #private;
    constructor(topic: string, marker: Marker, receiveTime: bigint | undefined, renderer: Renderer);
    dispose(): void;
    update(newMarker: Marker, receiveTime: bigint | undefined): void;
}
