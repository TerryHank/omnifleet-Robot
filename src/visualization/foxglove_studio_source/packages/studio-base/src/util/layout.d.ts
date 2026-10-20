import { MosaicUpdate, MosaicNode, MosaicPath } from "react-mosaic-component";
import { MosaicKey } from "react-mosaic-component/lib/types";
import { ConfigsPayload, SaveConfigsPayload } from "@foxglove/studio-base/context/CurrentLayoutContext/actions";
import { TabLocation, TabPanelConfig } from "@foxglove/studio-base/types/layouts";
import { PanelConfig, MosaicDropTargetPosition, SavedProps } from "@foxglove/studio-base/types/panels";
/** Key injected into panel configs for user-selected title (overrides setDefaultPanelTitle) */
export declare const PANEL_TITLE_CONFIG_KEY = "foxglovePanelTitle";
export declare function getPanelIdForType(type: string): string;
export declare function getPanelTypeFromId(id: string): string;
export declare function isTabPanel(panelId: string): boolean;
export declare function isTabPanelConfig(config: PanelConfig | undefined): config is TabPanelConfig;
export declare function getPathFromNode<T extends MosaicKey>(node: T | undefined, tree: MosaicNode<T> | null, // eslint-disable-line no-restricted-syntax
path?: MosaicPath): MosaicPath;
export declare function inlineTabPanelLayouts(layout: MosaicNode<string>, savedProps: SavedProps, preserveTabPanelIds: readonly string[]): MosaicNode<string>;
export declare const getParentTabPanelByPanelId: (savedProps: SavedProps) => {
    [key: string]: string;
};
export declare const getSaveConfigsPayloadForAddedPanel: ({ id, config, savedProps, }: {
    id: string;
    config: PanelConfig;
    savedProps: SavedProps;
}) => SaveConfigsPayload;
export declare function getPanelIdsInsideTabPanels(panelIds: string[], savedProps: SavedProps): string[];
export declare const DEFAULT_TAB_PANEL_CONFIG: TabPanelConfig;
export declare function getAllPanelIds(layout: MosaicNode<string>, savedProps: SavedProps): string[];
export declare const validateTabPanelConfig: (config?: PanelConfig) => config is TabPanelConfig;
export declare const updateTabPanelLayout: (layout: MosaicNode<string> | undefined, tabPanelConfig: TabPanelConfig) => TabPanelConfig;
export declare const removePanelFromTabPanel: (path: MosaicPath | undefined, config: TabPanelConfig, tabId: string) => SaveConfigsPayload;
export declare const createAddUpdates: (tree: MosaicNode<string> | undefined, panelId: string, newPath: MosaicPath, position: MosaicDropTargetPosition) => MosaicUpdate<string>[];
export declare const addPanelToTab: (insertedPanelId: string, destinationPath: MosaicPath | undefined, destinationPosition: MosaicDropTargetPosition | undefined, tabConfig: PanelConfig | undefined, tabId: string) => SaveConfigsPayload;
export declare const reorderTabWithinTabPanel: ({ source, target, savedProps, }: {
    source: TabLocation;
    target: TabLocation;
    savedProps: SavedProps;
}) => SaveConfigsPayload;
export declare const moveTabBetweenTabPanels: ({ source, target, savedProps, }: {
    source: TabLocation;
    target: TabLocation;
    savedProps: SavedProps;
}) => SaveConfigsPayload;
export declare const replaceAndRemovePanels: (panelArgs: {
    originalId?: string;
    newId?: string;
    idsToRemove?: readonly string[];
}, layout: MosaicNode<string>) => MosaicNode<string> | undefined;
export declare function getConfigsForNestedPanelsInsideTab(panelIdToReplace: string | undefined, tabPanelId: string | undefined, panelIdsToRemove: readonly string[], savedProps: SavedProps): ConfigsPayload[];
