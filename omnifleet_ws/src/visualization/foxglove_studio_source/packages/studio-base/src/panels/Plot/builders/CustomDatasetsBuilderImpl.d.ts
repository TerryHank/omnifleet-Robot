import { Immutable, Time } from "@foxglove/studio";
import { CsvDataset, GetViewportDatasetsResult, SeriesConfigKey, SeriesItem, Viewport } from "./IDatasetsBuilder";
import { OriginalValue } from "../datum";
export type ValueItem = {
    value: number;
    originalValue: OriginalValue;
    receiveTime: Time;
};
type ResetSeriesFullAction = {
    type: "reset-full";
    series: SeriesConfigKey;
};
type ResetSeriesCurrentAction = {
    type: "reset-current";
    series: SeriesConfigKey;
};
type ResetCurrentXAction = {
    type: "reset-current-x";
};
type ResetFullXAction = {
    type: "reset-full-x";
};
type UpdateCurrentXAction = {
    type: "append-current-x";
    items: ValueItem[];
};
type UpdateFullXAction = {
    type: "append-full-x";
    items: ValueItem[];
};
type UpdateSeriesCurrentAction = {
    type: "append-current";
    series: SeriesConfigKey;
    items: ValueItem[];
};
type UpdateSeriesFullAction = {
    type: "append-full";
    series: SeriesConfigKey;
    items: ValueItem[];
};
type UpdateSeriesConfigAction = {
    type: "update-series-config";
    seriesItems: SeriesItem[];
};
export type UpdateDataAction = UpdateSeriesConfigAction | ResetSeriesFullAction | ResetSeriesCurrentAction | ResetCurrentXAction | ResetFullXAction | UpdateCurrentXAction | UpdateFullXAction | UpdateSeriesCurrentAction | UpdateSeriesFullAction;
export declare class CustomDatasetsBuilderImpl {
    #private;
    updateData(actions: Immutable<UpdateDataAction[]>): void;
    getViewportDatasets(viewport: Immutable<Viewport>): GetViewportDatasetsResult;
    getCsvData(): CsvDataset[];
}
export {};
