import { RenderableMarker } from "./RenderableMarker";
import type { Renderer } from "../../Renderer";
import { MarkerType, Marker } from "../../ros";
/**
 * An object pool for RenderableMarker subclass objects.
 */
export declare class MarkerPool {
    #private;
    private renderer;
    constructor(renderer: Renderer);
    acquire<T extends MarkerType>(type: T, topic: string, marker: Marker, receiveTime: bigint | undefined): RenderableMarker;
    release(renderable: RenderableMarker): void;
    dispose(): void;
}
