/// <reference types="react" />
import { LayoutData } from "@foxglove/studio-base/context/CurrentLayoutContext/actions";
import { Player, PlayerMetricsCollectorInterface } from "@foxglove/studio-base/players/types";
import { RegisteredIconNames } from "@foxglove/studio-base/types/Icons";
export type DataSourceFactoryInitializeArgs = {
    metricsCollector: PlayerMetricsCollectorInterface;
    file?: File;
    files?: File[];
    params?: Record<string, string | undefined>;
};
export type DataSourceFactoryType = "file" | "connection" | "sample";
export type Field = {
    id: string;
    label: string;
    defaultValue?: string;
    placeholder?: string;
    description?: string;
    /**
     * Optional validate function
     *
     * The function is called with a value and can return an Error if the value should
     * be rejected. If the function returns `undefined`, then the value is accepted.
     */
    validate?: (value: string) => Error | undefined;
};
export interface IDataSourceFactory {
    id: string;
    legacyIds?: string[];
    type: DataSourceFactoryType;
    displayName: string;
    iconName?: RegisteredIconNames;
    description?: string;
    docsLinks?: {
        label?: string;
        url: string;
    }[];
    disabledReason?: string | JSX.Element;
    badgeText?: string;
    hidden?: boolean;
    warning?: string | JSX.Element;
    sampleLayout?: LayoutData;
    formConfig?: {
        fields: Field[];
    };
    supportedFileTypes?: string[];
    supportsMultiFile?: boolean;
    initialize: (args: DataSourceFactoryInitializeArgs) => Player | undefined;
}
/**
 * Recently selected source information
 *
 * The _id_ is opaque and up to the PlayerSelectionContext implementation.
 */
export type RecentSource = {
    id: string;
    title: string;
    label?: string;
};
type FileDataSourceArgs = {
    type: "file";
    files?: File[];
    handle?: FileSystemFileHandle;
};
type ConnectionDataSourceArgs = {
    type: "connection";
    params?: Record<string, string | undefined>;
};
export type DataSourceArgs = FileDataSourceArgs | ConnectionDataSourceArgs;
/**
 * PlayerSelectionContext exposes the available data sources and a function to set the current data source
 */
export interface PlayerSelection {
    selectSource: (sourceId: string, args?: DataSourceArgs) => void;
    selectRecent: (recentId: string) => void;
    /** Currently selected data source */
    selectedSource?: IDataSourceFactory;
    /** List of available data sources */
    availableSources: readonly IDataSourceFactory[];
    /** Recently selected sources */
    recentSources: readonly RecentSource[];
}
declare const PlayerSelectionContext: import("react").Context<PlayerSelection>;
export declare function usePlayerSelection(): PlayerSelection;
export default PlayerSelectionContext;
