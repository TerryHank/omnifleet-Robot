import { Immutable, SettingsTreeNode, SettingsTreeNodes } from "@foxglove/studio";
/**
 * Filters and sorts roots to prepare them for rendering.
 */
export declare function prepareSettingsNodes(roots: Immutable<SettingsTreeNodes>): Immutable<Array<[string, SettingsTreeNode]>>;
/**
 * Recursively filter out nodes that don't match the given filter.
 */
export declare function filterTreeNodes(nodes: Immutable<SettingsTreeNodes>, filter: string): Immutable<SettingsTreeNodes>;
