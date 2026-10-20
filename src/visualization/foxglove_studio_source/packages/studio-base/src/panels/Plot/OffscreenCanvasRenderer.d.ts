import type { Theme } from "@mui/material";
import { Immutable } from "@foxglove/studio";
import { Bounds } from "@foxglove/studio-base/types/Bounds";
import { Dataset, HoverElement, Scale, UpdateAction } from "./ChartRenderer";
export declare class OffscreenCanvasRenderer {
    #private;
    constructor(canvas: OffscreenCanvas, theme: Theme);
    update(action: Immutable<UpdateAction>): Promise<Bounds | undefined>;
    getElementsAtPixel(pixel: {
        x: number;
        y: number;
    }): Promise<HoverElement[]>;
    updateDatasets(datasets: Dataset[]): Promise<Scale | undefined>;
}
