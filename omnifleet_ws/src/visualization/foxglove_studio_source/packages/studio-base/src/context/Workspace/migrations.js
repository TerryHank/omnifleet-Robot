// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
export function migrateV0WorkspaceState(oldState, _version) {
    // Currently v0 is the only obsolete state. If we do more migrations this
    // needs to consider the version number.
    const v0State = oldState;
    const migrated = {
        dialogs: {
            dataSource: {
                activeDataSource: undefined,
                item: undefined,
                open: false,
            },
            preferences: {
                initialTab: undefined,
                open: false,
            },
        },
        featureTours: {
            active: undefined,
            shown: v0State.featureTours.shown,
        },
        sidebars: {
            left: {
                item: v0State.leftSidebarItem,
                open: v0State.leftSidebarOpen,
                size: v0State.leftSidebarSize,
            },
            right: {
                item: v0State.rightSidebarItem,
                open: v0State.rightSidebarOpen,
                size: v0State.rightSidebarSize,
            },
        },
        playbackControls: {
            repeat: v0State.playbackControls.repeat,
        },
    };
    return migrated;
}
