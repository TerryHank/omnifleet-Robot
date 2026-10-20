import EventEmitter from "eventemitter3";
import { Immutable } from "@foxglove/studio";
import { Bounds1D } from "@foxglove/studio-base/components/TimeBasedChart/types";
import { GlobalVariables } from "@foxglove/studio-base/hooks/useGlobalVariables";
import { PlayerState } from "@foxglove/studio-base/players/types";
import { InteractionEvent, Scale } from "./ChartRenderer";
import { OffscreenCanvasRenderer } from "./OffscreenCanvasRenderer";
import { CsvDataset, IDatasetsBuilder } from "./builders/IDatasetsBuilder";
import { PlotConfig } from "./config";
type EventTypes = {
    timeseriesBounds(bounds: Immutable<Bounds1D>): void;
    /** X scale changed. */
    xScaleChanged(scale: Scale | undefined): void;
    /** Current values changed (for displaying in the legend) */
    currentValuesChanged(values: readonly unknown[]): void;
    /** Paths with mismatched data lengths were detected */
    pathsWithMismatchedDataLengthsChanged(pathsWithMismatchedDataLengths: string[]): void;
    /** Rendering updated the viewport. `canReset` is true if the viewport can be reset. */
    viewportChange(canReset: boolean): void;
};
/**
 * PlotCoordinator interfaces commands and updates between the dataset builder and the chart
 * renderer.
 */
export declare class PlotCoordinator extends EventEmitter<EventTypes> {
    #private;
    constructor(renderer: OffscreenCanvasRenderer, builder: IDatasetsBuilder);
    /** Stop the coordinator from sending any future updates to the renderer. */
    destroy(): void;
    handlePlayerState(state: Immutable<PlayerState>): void;
    handleConfig(config: Immutable<PlotConfig>, colorScheme: "light" | "dark", globalVariables: GlobalVariables): void;
    setGlobalBounds(bounds: Immutable<Bounds1D> | undefined): void;
    setZoomMode(mode: "x" | "xy" | "y"): void;
    resetBounds(): void;
    setSize(size: {
        width: number;
        height: number;
    }): void;
    addInteractionEvent(ev: InteractionEvent): void;
    /** Get the plot x value at the canvas pixel x location */
    getXValueAtPixel(pixelX: number): number;
    /** Get the entire data for all series */
    getCsvData(): Promise<CsvDataset[]>;
}
export {};
