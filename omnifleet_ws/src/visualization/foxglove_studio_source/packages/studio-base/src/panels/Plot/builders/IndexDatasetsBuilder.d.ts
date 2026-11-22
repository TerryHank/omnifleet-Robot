import { Immutable } from "@foxglove/studio";
import { PlayerState } from "@foxglove/studio-base/players/types";
import { CsvDataset, GetViewportDatasetsResult, HandlePlayerStateResult, IDatasetsBuilder, SeriesItem } from "./IDatasetsBuilder";
export declare class IndexDatasetsBuilder implements IDatasetsBuilder {
    #private;
    handlePlayerState(state: Immutable<PlayerState>): HandlePlayerStateResult | undefined;
    setSeries(series: Immutable<SeriesItem[]>): void;
    getViewportDatasets(): Promise<GetViewportDatasetsResult>;
    getCsvData(): Promise<CsvDataset[]>;
}
