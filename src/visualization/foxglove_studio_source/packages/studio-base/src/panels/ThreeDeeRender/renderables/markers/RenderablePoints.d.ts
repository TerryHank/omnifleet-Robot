import { RenderableMarker } from "./RenderableMarker";
import type { IRenderer } from "../../IRenderer";
import { Marker } from "../../ros";
export declare class RenderablePoints extends RenderableMarker {
    #private;
    constructor(topic: string, marker: Marker, receiveTime: bigint | undefined, renderer: IRenderer);
    dispose(): void;
    update(newMarker: Marker, receiveTime: bigint | undefined): void;
}
