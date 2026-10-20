import { Immutable, Time } from "@foxglove/studio";
import { Topic } from "@foxglove/studio-base/players/types";
import { RosDatatypes } from "@foxglove/studio-base/types/RosDatatypes";
export type DataSourceInfo = {
    topics: readonly Topic[];
    datatypes: RosDatatypes;
    capabilities: string[];
    startTime?: Time;
    playerId: string;
};
/**
 * Data source info" encapsulates **rarely-changing** metadata about the source from which
 * Foxglove Studio is loading data.
 *
 * A data source might be a local file, a remote file, or a streaming source.
 */
export declare function useDataSourceInfo(): Immutable<DataSourceInfo>;
