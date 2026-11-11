import { SaveConfig } from "@foxglove/studio-base/types/panels";
import { PlotPath, PlotConfig } from "./config";
export declare const DEFAULT_PATH: PlotPath;
export declare function usePlotPanelSettings(config: PlotConfig, saveConfig: SaveConfig<PlotConfig>, focusedPath?: readonly string[]): void;
