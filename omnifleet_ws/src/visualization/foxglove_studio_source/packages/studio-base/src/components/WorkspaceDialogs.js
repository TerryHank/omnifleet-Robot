import { jsx as _jsx, Fragment as _Fragment } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { AppSettingsDialog } from "@foxglove/studio-base/components/AppSettingsDialog";
import { useWorkspaceStore, } from "@foxglove/studio-base/context/Workspace/WorkspaceContext";
import { useWorkspaceActions } from "../context/Workspace/useWorkspaceActions";
const selectWorkspacePrefsDialogOpen = (store) => store.dialogs.preferences.open;
/**
 * Encapsulates dialogs shown and controlled at workspace level.
 */
export function WorkspaceDialogs() {
    const prefsDialogOpen = useWorkspaceStore(selectWorkspacePrefsDialogOpen);
    const { dialogActions } = useWorkspaceActions();
    return (_jsx(_Fragment, { children: prefsDialogOpen && (_jsx(AppSettingsDialog, { id: "app-settings-dialog", open: true, onClose: () => {
                dialogActions.preferences.close();
            } })) }));
}
