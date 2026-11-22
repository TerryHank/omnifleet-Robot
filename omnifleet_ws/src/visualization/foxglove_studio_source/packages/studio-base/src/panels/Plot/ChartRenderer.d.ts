import { ChartDataset, ScatterDataPoint } from "chart.js";
import { Immutable } from "@foxglove/studio";
import { Bounds, Bounds1D } from "@foxglove/studio-base/types/Bounds";
import { OriginalValue } from "./datum";
export type Scale = {
    min: number;
    max: number;
    left: number;
    right: number;
};
type BaseInteractionEvent = {
    cancelable: boolean;
    deltaY: number;
    deltaX: number;
    boundingClientRect: DOMRect;
};
type MouseBase = BaseInteractionEvent & {
    clientX: number;
    clientY: number;
};
type WheelInteractionEvent = {
    type: "wheel";
} & BaseInteractionEvent & MouseBase;
type PanStartInteractionEvent = {
    type: "panstart";
} & BaseInteractionEvent & {
    center: {
        x: number;
        y: number;
    };
};
type PanMoveInteractionEvent = {
    type: "panmove";
} & BaseInteractionEvent;
type PanEndInteractionEvent = {
    type: "panend";
} & BaseInteractionEvent;
export type InteractionEvent = WheelInteractionEvent | PanStartInteractionEvent | PanMoveInteractionEvent | PanEndInteractionEvent;
export type Datum = ScatterDataPoint & {
    value?: OriginalValue;
};
export type Dataset = ChartDataset<"scatter", Datum[]>;
export type HoverElement = {
    data: Datum;
    configIndex: number;
};
export type Size = {
    width: number;
    height: number;
};
export type UpdateAction = {
    type: "update";
    size?: {
        width: number;
        height: number;
    };
    showXAxisLabels?: boolean;
    showYAxisLabels?: boolean;
    xBounds?: Partial<Bounds1D>;
    yBounds?: Partial<Bounds1D>;
    zoomMode?: "x" | "y" | "xy";
    referenceLines?: {
        color: string;
        value: number;
    }[];
    interactionEvents?: InteractionEvent[];
};
export declare class ChartRenderer {
    #private;
    constructor(args: {
        canvas: OffscreenCanvas;
        devicePixelRatio: number;
        gridColor: string;
        tickColor: string;
    });
    update(action: Immutable<UpdateAction>): Bounds | undefined;
    getElementsAtPixel(pixel: {
        x: number;
        y: number;
    }): HoverElement[];
    updateDatasets(datasets: Dataset[]): Scale | undefined;
}
export {};
