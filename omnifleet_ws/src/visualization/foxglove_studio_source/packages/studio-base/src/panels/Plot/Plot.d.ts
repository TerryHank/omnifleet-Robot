/// <reference types="react" />
import { SaveConfig } from "@foxglove/studio-base/types/panels";
import { PlotConfig } from "./config";
export declare const defaultSidebarDimension = 240;
type Props = {
    config: PlotConfig;
    saveConfig: SaveConfig<PlotConfig>;
};
export declare function Plot(props: Props): JSX.Element;
export {};
