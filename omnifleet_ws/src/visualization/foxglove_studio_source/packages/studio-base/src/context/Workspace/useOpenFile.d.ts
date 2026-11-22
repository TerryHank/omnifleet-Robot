import { IDataSourceFactory } from "@foxglove/studio-base/context/PlayerSelectionContext";
export declare function useOpenFile(sources: readonly IDataSourceFactory[]): () => Promise<void>;
