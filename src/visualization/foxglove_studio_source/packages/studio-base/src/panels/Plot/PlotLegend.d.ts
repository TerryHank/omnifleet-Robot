/// <reference types="react" />
import { Immutable } from "@foxglove/studio";
import { SaveConfig } from "@foxglove/studio-base/types/panels";
import type { PlotCoordinator } from "./PlotCoordinator";
import { PlotPath, PlotConfig } from "./config";
type Props = Immutable<{
    coordinator: PlotCoordinator | undefined;
    legendDisplay: "floating" | "top" | "left";
    onClickPath: (index: number) => void;
    paths: PlotPath[];
    saveConfig: SaveConfig<PlotConfig>;
    showLegend: boolean;
    sidebarDimension: number;
    showValues: boolean;
    hoveredValuesBySeriesIndex?: string[];
}>;
declare function PlotLegendComponent(props: Props): JSX.Element;
export declare const PlotLegend: import("react").MemoExoticComponent<typeof PlotLegendComponent>;
export {};
