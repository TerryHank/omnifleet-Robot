import { Time } from "@foxglove/rostime";
import { Immutable } from "@foxglove/studio";
import { MessagePathDataItem } from "@foxglove/studio-base/components/MessagePathSyntax/useCachedGetMessagePathDataItems";
import { MessageEvent } from "@foxglove/studio-base/players/types";
import { PANEL_TITLE_CONFIG_KEY } from "@foxglove/studio-base/util/layout";
import { TimestampMethod } from "@foxglove/studio-base/util/time";
export type Messages = Record<string, MessageEvent[]>;
export type BasePlotPath = {
    value: string;
    enabled: boolean;
};
export type PlotPath = BasePlotPath & {
    color?: string;
    label?: string;
    timestampMethod: TimestampMethod;
    showLine?: boolean;
    lineSize?: number;
};
export type PlotXAxisVal = "timestamp" | "index" | "custom" | "currentCustom";
export type PlotDataItem = {
    queriedData: MessagePathDataItem[];
    receiveTime: Time;
    headerStamp?: Time;
};
/**
 * A "reference line" plot path is a numeric value. It creates a horizontal line on the plot at the
 * specified value.
 * @returns true if the series config is a reference line
 */
export declare function isReferenceLinePlotPathType(path: Immutable<PlotPath>): boolean;
export declare function plotPathDisplayName(path: Readonly<PlotPath>, index: number): string;
type DeprecatedPlotConfig = {
    showSidebar?: boolean;
    sidebarWidth?: number;
};
export type PlotConfig = DeprecatedPlotConfig & {
    paths: PlotPath[];
    minXValue?: number;
    maxXValue?: number;
    minYValue?: string | number;
    maxYValue?: string | number;
    showLegend: boolean;
    legendDisplay: "floating" | "top" | "left" | "none";
    showPlotValuesInLegend: boolean;
    showXAxisLabels: boolean;
    showYAxisLabels: boolean;
    isSynced: boolean;
    xAxisVal: PlotXAxisVal;
    xAxisPath?: BasePlotPath;
    followingViewWidth?: number;
    sidebarDimension: number;
    [PANEL_TITLE_CONFIG_KEY]?: string;
};
export {};
