/// <reference types="hammerjs" />
import { ChartData, ChartOptions, ChartType, InteractionModeFunction } from "chart.js";
import { RpcElement, RpcScales } from "@foxglove/studio-base/components/Chart/types";
import { TypedChartData } from "../types";
export type InitOpts = {
    id: string;
    node: {
        canvas: HTMLCanvasElement;
    };
    type: ChartType;
    data: ChartData<"scatter">;
    options: ChartOptions;
    devicePixelRatio: number;
    fontLoaded: Promise<FontFace>;
};
declare module "chart.js" {
    interface InteractionModeMap {
        lastX: InteractionModeFunction;
    }
}
export default class ChartJSManager {
    #private;
    constructor(initOpts: InitOpts);
    init({ id, node, type, data, options, devicePixelRatio, fontLoaded, }: InitOpts): Promise<void>;
    wheel(event: WheelEvent): RpcScales;
    mousedown(event: MouseEvent): RpcScales;
    mousemove(event: MouseEvent): RpcScales;
    mouseup(event: MouseEvent): RpcScales;
    panstart(event: HammerInput): RpcScales;
    panmove(event: HammerInput): RpcScales;
    panend(event: HammerInput): RpcScales;
    update({ options, width, height, isBoundsReset, data, typedData, }: {
        options?: ChartOptions;
        width?: number;
        height?: number;
        isBoundsReset: boolean;
        data?: ChartData<"scatter">;
        typedData?: TypedChartData;
    }): RpcScales;
    destroy(): void;
    getElementsAtEvent({ event }: {
        event: MouseEvent;
    }): RpcElement[];
    getDatalabelAtEvent({ event }: {
        event: Event;
    }): unknown;
    getScales(): RpcScales;
}
