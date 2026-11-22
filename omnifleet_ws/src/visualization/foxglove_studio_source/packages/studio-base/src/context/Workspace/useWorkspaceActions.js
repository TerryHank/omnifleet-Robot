// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { produce } from "immer";
import * as _ from "lodash-es";
import { useCallback, useMemo } from "react";
import { useMountedState } from "react-use";
import { useGuaranteedContext } from "@foxglove/hooks";
import { useAnalytics } from "@foxglove/studio-base/context/AnalyticsContext";
import { useAppContext } from "@foxglove/studio-base/context/AppContext";
import { useCurrentLayoutActions, } from "@foxglove/studio-base/context/CurrentLayoutContext";
import { usePlayerSelection, } from "@foxglove/studio-base/context/PlayerSelectionContext";
import useCallbackWithToast from "@foxglove/studio-base/hooks/useCallbackWithToast";
import { AppEvent } from "@foxglove/studio-base/services/IAnalytics";
import { downloadTextFile } from "@foxglove/studio-base/util/download";
import { LeftSidebarItemKeys, RightSidebarItemKeys, WorkspaceContext, } from "./WorkspaceContext";
import { useOpenFile } from "./useOpenFile";
function setterValue(action, value) {
    if (action instanceof Function) {
        return action(value);
    }
    return action;
}
/**
 * Provides various actions to manipulate the workspace state.
 */
export function useWorkspaceActions() {
    const { setState } = useGuaranteedContext(WorkspaceContext);
    const { availableSources } = usePlayerSelection();
    const analytics = useAnalytics();
    const appContext = useAppContext();
    const isMounted = useMountedState();
    const { getCurrentLayoutState, setCurrentLayout } = useCurrentLayoutActions();
    const openFile = useOpenFile(availableSources);
    const set = useCallback((setter) => {
        setState(produce(setter));
    }, [setState]);
    const importLayoutFromFile = useCallbackWithToast(async () => {
        const fileHandles = await showOpenFilePicker({
            multiple: false,
            excludeAcceptAllOption: false,
            types: [
                {
                    description: "JSON 文件",
                    accept: {
                        "application/json": [".json"],
                    },
                },
            ],
        });
        if (!isMounted()) {
            return;
        }
        const file = await fileHandles[0].getFile();
        const content = await file.text();
        if (!isMounted()) {
            return;
        }
        let parsedState;
        try {
            parsedState = JSON.parse(content);
        }
        catch (err) {
            throw new Error(`${file.name} is not a valid layout: ${err.message}`);
        }
        if (typeof parsedState !== "object" || !parsedState) {
            throw new Error(`${file.name} is not a valid layout`);
        }
        const data = parsedState;
        // If there's an app context handler for this we let it take over from here
        if (appContext.importLayoutFile) {
            await appContext.importLayoutFile(file.name, data);
            return;
        }
        setCurrentLayout({ data });
        void analytics.logEvent(AppEvent.LAYOUT_IMPORT);
    }, [analytics, appContext, isMounted, setCurrentLayout]);
    const exportLayoutToFile = useCallback(() => {
        // Use a stable getter to fetch the current layout to avoid thrashing the
        // dependencies array for our hook.
        const layoutData = getCurrentLayoutState().selectedLayout?.data;
        if (!layoutData) {
            return;
        }
        const name = getCurrentLayoutState().selectedLayout?.name ?? "foxglove-layout";
        const content = JSON.stringify(layoutData, undefined, 2) ?? "";
        downloadTextFile(content, `${name}.json`);
        void analytics.logEvent(AppEvent.LAYOUT_EXPORT);
    }, [analytics, getCurrentLayoutState]);
    return useMemo(() => {
        return {
            dialogActions: {
                dataSource: {
                    close: () => {
                        set((draft) => {
                            draft.dialogs.dataSource = {
                                activeDataSource: undefined,
                                item: undefined,
                                open: false,
                            };
                        });
                    },
                    open: (selectedDataSourceDialogItem, dataSource) => {
                        set((draft) => {
                            // This cast is necessary to keep typescript from complaining about type depth.
                            draft.dialogs.dataSource.activeDataSource = dataSource;
                            draft.dialogs.dataSource.item = selectedDataSourceDialogItem;
                            draft.dialogs.dataSource.open = true;
                        });
                    },
                },
                openFile: {
                    open: openFile,
                },
                preferences: {
                    close: () => {
                        set((draft) => {
                            draft.dialogs.preferences = { open: false, initialTab: undefined };
                        });
                    },
                    open: (initialTab) => {
                        set((draft) => {
                            draft.dialogs.preferences = { open: true, initialTab };
                        });
                    },
                },
            },
            featureTourActions: {
                startTour: (tour) => {
                    set((draft) => {
                        draft.featureTours.active = tour;
                    });
                },
                finishTour: (tour) => {
                    set((draft) => {
                        draft.featureTours.active = undefined;
                        draft.featureTours.shown = _.union(draft.featureTours.shown, [tour]);
                    });
                },
            },
            openPanelSettings: () => {
                set((draft) => {
                    draft.sidebars.left.item = "panel-settings";
                    draft.sidebars.left.open = true;
                });
            },
            playbackControlActions: {
                setRepeat: (setter) => {
                    set((draft) => {
                        const repeat = setterValue(setter, draft.playbackControls.repeat);
                        draft.playbackControls.repeat = repeat;
                    });
                },
            },
            sidebarActions: {
                left: {
                    selectItem: (selectedLeftSidebarItem) => {
                        set((draft) => {
                            draft.sidebars.left.item = selectedLeftSidebarItem;
                            draft.sidebars.left.open = selectedLeftSidebarItem != undefined;
                        });
                    },
                    setOpen: (setter) => {
                        set((draft) => {
                            const leftSidebarOpen = setterValue(setter, draft.sidebars.left.open);
                            if (leftSidebarOpen) {
                                const oldItem = LeftSidebarItemKeys.find((item) => item === draft.sidebars.left.item);
                                draft.sidebars.left.open = leftSidebarOpen;
                                draft.sidebars.left.item = oldItem ?? "panel-settings";
                            }
                            else {
                                draft.sidebars.left.open = false;
                            }
                        });
                    },
                    setSize: (leftSidebarSize) => {
                        set((draft) => {
                            draft.sidebars.left.size = leftSidebarSize;
                        });
                    },
                },
                right: {
                    selectItem: (selectedRightSidebarItem) => {
                        set((draft) => {
                            draft.sidebars.right.item = selectedRightSidebarItem;
                            draft.sidebars.right.open = selectedRightSidebarItem != undefined;
                        });
                    },
                    setOpen: (setter) => {
                        set((draft) => {
                            const rightSidebarOpen = setterValue(setter, draft.sidebars.right.open);
                            const oldItem = RightSidebarItemKeys.find((item) => item === draft.sidebars.right.item);
                            if (rightSidebarOpen) {
                                draft.sidebars.right.open = rightSidebarOpen;
                                draft.sidebars.right.item = oldItem ?? "variables";
                            }
                            else {
                                draft.sidebars.right.open = false;
                            }
                        });
                    },
                    setSize: (rightSidebarSize) => {
                        set((draft) => {
                            draft.sidebars.right.size = rightSidebarSize;
                        });
                    },
                },
            },
            layoutActions: {
                importFromFile: importLayoutFromFile,
                exportToFile: exportLayoutToFile,
            },
        };
    }, [exportLayoutToFile, importLayoutFromFile, openFile, set]);
}
