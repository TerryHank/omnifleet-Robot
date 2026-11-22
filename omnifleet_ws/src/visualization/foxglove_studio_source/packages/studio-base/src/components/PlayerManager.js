import { jsx as _jsx, Fragment as _Fragment } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
//
// This file incorporates work covered by the following copyright and
// permission notice:
//
//   Copyright 2018-2021 Cruise LLC
//
//   This source code is licensed under the Apache License, Version 2.0,
//   found at http://www.apache.org/licenses/LICENSE-2.0
//   You may not use this file except in compliance with the License.
import { useSnackbar } from "notistack";
import { useCallback, useContext, useEffect, useMemo, useState } from "react";
import { useMountedState } from "react-use";
import { useWarnImmediateReRender } from "@foxglove/hooks";
import Logger from "@foxglove/log";
import { MessagePipelineProvider } from "@foxglove/studio-base/components/MessagePipeline";
import { useAnalytics } from "@foxglove/studio-base/context/AnalyticsContext";
import { useAppContext } from "@foxglove/studio-base/context/AppContext";
import { ExtensionCatalogContext } from "@foxglove/studio-base/context/ExtensionCatalogContext";
import PlayerSelectionContext from "@foxglove/studio-base/context/PlayerSelectionContext";
import useIndexedDbRecents from "@foxglove/studio-base/hooks/useIndexedDbRecents";
import AnalyticsMetricsCollector from "@foxglove/studio-base/players/AnalyticsMetricsCollector";
import { TopicAliasingPlayer, } from "@foxglove/studio-base/players/TopicAliasingPlayer/TopicAliasingPlayer";
const log = Logger.getLogger(__filename);
export default function PlayerManager(props) {
    const { children, playerSources } = props;
    useWarnImmediateReRender();
    const { wrapPlayer } = useAppContext();
    const isMounted = useMountedState();
    const analytics = useAnalytics();
    const metricsCollector = useMemo(() => new AnalyticsMetricsCollector(analytics), [analytics]);
    const [basePlayer, setBasePlayer] = useState();
    const { recents, addRecent } = useIndexedDbRecents();
    const topicAliasPlayer = useMemo(() => {
        if (!basePlayer) {
            return undefined;
        }
        return new TopicAliasingPlayer(basePlayer);
    }, [basePlayer]);
    // Update the alias functions when they change. We do not need to re-render the player manager
    // since nothing in the local state has changed.
    const extensionCatalogContext = useContext(ExtensionCatalogContext);
    useEffect(() => {
        // Stable empty alias functions if we don't have any
        const emptyAliasFunctions = [];
        // We only want to set alias functions on the player when the functions have changed
        let topicAliasFunctions = extensionCatalogContext.getState().installedTopicAliasFunctions ?? emptyAliasFunctions;
        topicAliasPlayer?.setAliasFunctions(topicAliasFunctions);
        return extensionCatalogContext.subscribe((state) => {
            if (topicAliasFunctions !== state.installedTopicAliasFunctions) {
                topicAliasFunctions = state.installedTopicAliasFunctions ?? emptyAliasFunctions;
                topicAliasPlayer?.setAliasFunctions(topicAliasFunctions);
            }
        });
    }, [extensionCatalogContext, topicAliasPlayer]);
    const player = useMemo(() => {
        if (!topicAliasPlayer) {
            return undefined;
        }
        return wrapPlayer(topicAliasPlayer);
    }, [topicAliasPlayer, wrapPlayer]);
    const { enqueueSnackbar } = useSnackbar();
    const [selectedSource, setSelectedSource] = useState();
    const selectSource = useCallback(async (sourceId, args) => {
        log.debug(`Select Source: ${sourceId}`);
        const foundSource = playerSources.find((source) => source.id === sourceId || source.legacyIds?.includes(sourceId));
        if (!foundSource) {
            enqueueSnackbar(`Unknown data source: ${sourceId}`, { variant: "warning" });
            return;
        }
        metricsCollector.setProperty("player", sourceId);
        setSelectedSource(foundSource);
        // Sample sources don't need args or prompts to initialize
        if (foundSource.type === "sample") {
            const newPlayer = foundSource.initialize({
                metricsCollector,
            });
            setBasePlayer(newPlayer);
            return;
        }
        if (!args) {
            enqueueSnackbar("Unable to initialize player: no args", { variant: "error" });
            setSelectedSource(undefined);
            return;
        }
        try {
            switch (args.type) {
                case "connection": {
                    const newPlayer = foundSource.initialize({
                        metricsCollector,
                        params: args.params,
                    });
                    setBasePlayer(newPlayer);
                    if (args.params?.url) {
                        addRecent({
                            type: "connection",
                            sourceId: foundSource.id,
                            title: args.params.url,
                            label: foundSource.displayName,
                            extra: args.params,
                        });
                    }
                    return;
                }
                case "file": {
                    const handle = args.handle;
                    const files = args.files;
                    // files we can try loading immediately
                    // We do not add these to recents entries because putting File in indexedb results in
                    // the entire file being stored in the database.
                    if (files) {
                        let file = files[0];
                        const fileList = [];
                        for (const curFile of files) {
                            file ??= curFile;
                            fileList.push(curFile);
                        }
                        const multiFile = foundSource.supportsMultiFile === true && fileList.length > 1;
                        const newPlayer = foundSource.initialize({
                            file: multiFile ? undefined : file,
                            files: multiFile ? fileList : undefined,
                            metricsCollector,
                        });
                        setBasePlayer(newPlayer);
                        return;
                    }
                    else if (handle) {
                        const permission = await handle.queryPermission({ mode: "read" });
                        if (!isMounted()) {
                            return;
                        }
                        if (permission !== "granted") {
                            const newPerm = await handle.requestPermission({ mode: "read" });
                            if (newPerm !== "granted") {
                                throw new Error(`Permission denied: ${handle.name}`);
                            }
                        }
                        const file = await handle.getFile();
                        if (!isMounted()) {
                            return;
                        }
                        const newPlayer = foundSource.initialize({
                            file,
                            metricsCollector,
                        });
                        setBasePlayer(newPlayer);
                        addRecent({
                            type: "file",
                            title: handle.name,
                            sourceId: foundSource.id,
                            handle,
                        });
                        return;
                    }
                }
            }
            enqueueSnackbar("Unable to initialize player", { variant: "error" });
        }
        catch (error) {
            enqueueSnackbar(error.message, { variant: "error" });
        }
    }, [playerSources, metricsCollector, enqueueSnackbar, isMounted, addRecent]);
    // Select a recent entry by id
    // necessary to pull out callback creation to avoid capturing the initial player in closure context
    // eslint-disable-next-line react-hooks/exhaustive-deps
    const selectRecent = useCallback(createSelectRecentCallback(recents, selectSource, enqueueSnackbar), [recents, enqueueSnackbar, selectSource]);
    // Make a RecentSources array for the PlayerSelectionContext
    const recentSources = useMemo(() => {
        return recents.map((item) => {
            return { id: item.id, title: item.title, label: item.label };
        });
    }, [recents]);
    const value = {
        selectSource,
        selectRecent,
        selectedSource,
        availableSources: playerSources,
        recentSources,
    };
    return (_jsx(_Fragment, { children: _jsx(PlayerSelectionContext.Provider, { value: value, children: _jsx(MessagePipelineProvider, { player: player, children: children }) }) }));
}
/**
 * This was moved out of the PlayerManager function due to a memory leak occurring in memoized state of Start.tsx
 * that was retaining old player instances. Having this callback be defined within the PlayerManager makes it store the
 * player at instantiation within the closure context. That callback is then stored in the memoized state with its closure context.
 * The callback is updated when the player changes but part of the `Start.tsx` holds onto the formerly memoized state for an
 * unknown reason.
 * To make this function safe from storing old closure contexts in old memoized state in components where it
 * is used, it has been moved out of the PlayerManager function.
 */
function createSelectRecentCallback(recents, selectSource, enqueueSnackbar) {
    return (recentId) => {
        // find the recent from the list and initialize
        const foundRecent = recents.find((value) => value.id === recentId);
        if (!foundRecent) {
            enqueueSnackbar(`Failed to restore recent: ${recentId}`, { variant: "error" });
            return;
        }
        switch (foundRecent.type) {
            case "connection": {
                void selectSource(foundRecent.sourceId, {
                    type: "connection",
                    params: foundRecent.extra,
                });
                break;
            }
            case "file": {
                void selectSource(foundRecent.sourceId, {
                    type: "file",
                    handle: foundRecent.handle,
                });
            }
        }
    };
}
