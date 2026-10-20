import EventEmitter from "eventemitter3";
import { SettingsTreeAction, SettingsTreeNode, SettingsTreeNodes } from "@foxglove/studio";
import { LayerErrors, Path } from "./LayerErrors";
export type ActionHandler = (action: SettingsTreeAction) => void;
export type SettingsTreeNodeWithActionHandler = SettingsTreeNode & {
    handler?: ActionHandler;
};
export type SettingsTreeEntry = {
    path: Path;
    node: SettingsTreeNodeWithActionHandler;
};
export type SettingsManagerEvents = {
    update: () => void;
};
type NodeValidator = (entry: SettingsTreeEntry, errorState: LayerErrors) => void;
export declare class SettingsManager extends EventEmitter<SettingsManagerEvents> {
    #private;
    errors: LayerErrors;
    constructor(baseTree: SettingsTreeNodes);
    setNodesForKey(key: string, nodes: SettingsTreeEntry[]): void;
    setLabel(path: Path, label: string): void;
    clearChildren(path: Path): void;
    tree(): SettingsTreeNodes;
    handleAction: (action: SettingsTreeAction) => void;
    /** Add Validator function that can run over nodes `set` on the tree and update error state accordingly */
    addNodeValidator: (nodeValidator: NodeValidator) => void;
    removeNodeValidator: (nodeValidator: NodeValidator) => void;
    handleErrorUpdate: (path: Path) => void;
}
export {};
