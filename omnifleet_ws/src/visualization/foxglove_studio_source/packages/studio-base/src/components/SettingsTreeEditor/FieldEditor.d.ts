/// <reference types="react" />
import { Immutable, SettingsTreeAction, SettingsTreeField } from "@foxglove/studio";
declare function FieldEditorComponent({ actionHandler, field, path, }: {
    actionHandler: (action: SettingsTreeAction) => void;
    field: Immutable<SettingsTreeField>;
    path: readonly string[];
}): JSX.Element;
export declare const FieldEditor: import("react").MemoExoticComponent<typeof FieldEditorComponent>;
export {};
