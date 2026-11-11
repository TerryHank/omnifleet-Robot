/// <reference types="react" />
import { SettingsTreeNodeAction } from "@foxglove/studio";
export declare function NodeActionsMenu({ actions, onSelectAction, }: {
    actions: readonly SettingsTreeNodeAction[];
    onSelectAction: (actionId: string) => void;
}): JSX.Element;
