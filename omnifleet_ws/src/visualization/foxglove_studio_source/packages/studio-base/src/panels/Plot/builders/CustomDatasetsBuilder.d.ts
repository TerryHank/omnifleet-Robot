import { MessagePath } from "@foxglove/message-path";
import { Immutable } from "@foxglove/studio";
import { PlayerState } from "@foxglove/studio-base/players/types";
import { CsvDataset, GetViewportDatasetsResult, HandlePlayerStateResult, IDatasetsBuilder, SeriesItem, Viewport } from "./IDatasetsBuilder";
export declare class CustomDatasetsBuilder implements IDatasetsBuilder {
    #private;
    constructor();
    handlePlayerState(state: Immutable<PlayerState>): HandlePlayerStateResult | undefined;
    setXPath(path: Immutable<MessagePath> | undefined): void;
    setSeries(series: Immutable<SeriesItem[]>): void;
    getViewportDatasets(viewport: Immutable<Viewport>): Promise<GetViewportDatasetsResult>;
    getCsvData(): Promise<CsvDataset[]>;
}
