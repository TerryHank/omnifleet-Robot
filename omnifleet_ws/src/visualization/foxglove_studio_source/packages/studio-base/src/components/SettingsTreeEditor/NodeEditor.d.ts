/// <reference types="react" />
import { Immutable, SettingsTreeAction, SettingsTreeNode } from "@foxglove/studio";
type NodeEditorProps = {
    actionHandler: (action: SettingsTreeAction) => void;
    defaultOpen?: boolean;
    filter?: string;
    focusedPath?: readonly string[];
    path: readonly string[];
    settings?: Immutable<SettingsTreeNode>;
};
declare function NodeEditorComponent(props: NodeEditorProps): JSX.Element;
export declare const NodeEditor: import("react").MemoExoticComponent<typeof NodeEditorComponent>;
export {};
