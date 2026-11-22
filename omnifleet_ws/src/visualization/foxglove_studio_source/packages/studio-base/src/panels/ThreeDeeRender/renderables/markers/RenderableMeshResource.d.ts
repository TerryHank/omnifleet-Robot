import { RenderableMarker } from "./RenderableMarker";
import type { IRenderer } from "../../IRenderer";
import { Marker } from "../../ros";
export declare class RenderableMeshResource extends RenderableMarker {
    #private;
    constructor(topic: string, marker: Marker, receiveTime: bigint | undefined, renderer: IRenderer, options?: {
        referenceUrl?: string;
    });
    dispose(): void;
    update(newMarker: Marker, receiveTime: bigint | undefined, forceLoad?: boolean): void;
}
