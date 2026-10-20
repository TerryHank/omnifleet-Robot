import { Immutable, Time } from "@foxglove/studio";
import { MessageBlock, PlayerState } from "@foxglove/studio-base/players/types";
import { CsvDataset, GetViewportDatasetsResult, HandlePlayerStateResult, IDatasetsBuilder, SeriesItem, Viewport } from "./IDatasetsBuilder";
/**
 * TimestampDatasetsBuilder builds timeseries datasets.
 *
 * It supports full (preload) data and current frame data. The series datums are extracted from
 * input player states and sent to the worker. The worker accumulates the data and provides
 * downsampled data.
 */
export declare class TimestampDatasetsBuilder implements IDatasetsBuilder {
    #private;
    constructor();
    handlePlayerState(state: Immutable<PlayerState>): HandlePlayerStateResult | undefined;
    handleBlocks(startTime: Immutable<Time>, blocks: Immutable<(MessageBlock | undefined)[]>, progress: () => Promise<boolean>): Promise<void>;
    setSeries(series: Immutable<SeriesItem[]>): void;
    getViewportDatasets(viewport: Immutable<Viewport>): Promise<GetViewportDatasetsResult>;
    getCsvData(): Promise<CsvDataset[]>;
}
