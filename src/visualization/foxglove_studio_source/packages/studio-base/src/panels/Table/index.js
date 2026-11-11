import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
//
// This file incorporates work covered by the following copyright and
// permission notice:
//
//   Copyright 2020-2021 Cruise LLC
//
//   This source code is licensed under the Apache License, Version 2.0,
//   found at http://www.apache.org/licenses/LICENSE-2.0
//   You may not use this file except in compliance with the License.
import { useEffect } from "react";
import { makeStyles } from "tss-react/mui";
import { parseMessagePath } from "@foxglove/message-path";
import { useMessagesByTopic } from "@foxglove/studio-base/PanelAPI";
import EmptyState from "@foxglove/studio-base/components/EmptyState";
import MessagePathInput from "@foxglove/studio-base/components/MessagePathSyntax/MessagePathInput";
import { useCachedGetMessagePathDataItems } from "@foxglove/studio-base/components/MessagePathSyntax/useCachedGetMessagePathDataItems";
import Panel from "@foxglove/studio-base/components/Panel";
import { usePanelContext } from "@foxglove/studio-base/components/PanelContext";
import PanelToolbar from "@foxglove/studio-base/components/PanelToolbar";
import Stack from "@foxglove/studio-base/components/Stack";
import Table from "./Table";
const useStyles = makeStyles()((theme) => ({
    toolbar: {
        paddingBlock: 0,
    },
    monospace: {
        fontFamily: theme.typography.fontMonospace,
    },
}));
function TablePanel({ config, saveConfig }) {
    const { topicPath } = config;
    const { classes } = useStyles();
    const onTopicPathChange = React.useCallback((newTopicPath) => {
        saveConfig({ topicPath: newTopicPath });
    }, [saveConfig]);
    const topicRosPath = React.useMemo(() => parseMessagePath(topicPath), [topicPath]);
    const topicName = topicRosPath?.topicName ?? "";
    const msgs = useMessagesByTopic({ topics: [topicName], historySize: 1 })[topicName];
    const cachedGetMessagePathDataItems = useCachedGetMessagePathDataItems([topicPath]);
    const msg = msgs?.[0];
    const cachedMessages = msg ? cachedGetMessagePathDataItems(topicPath, msg) ?? [] : [];
    const firstCachedMessage = cachedMessages[0];
    const { setMessagePathDropConfig } = usePanelContext();
    useEffect(() => {
        setMessagePathDropConfig({
            getDropStatus(paths) {
                if (paths.length !== 1) {
                    return { canDrop: false };
                }
                return { canDrop: true, effect: "replace" };
            },
            handleDrop(paths) {
                const path = paths[0];
                if (path) {
                    saveConfig({ topicPath: path.path });
                }
            },
        });
    }, [setMessagePathDropConfig, saveConfig]);
    return (_jsxs(Stack, { flex: "auto", overflow: "hidden", position: "relative", children: [_jsx(PanelToolbar, { className: classes.toolbar, children: _jsx(MessagePathInput, { index: 0, path: topicPath, onChange: onTopicPathChange }) }), topicPath.length === 0 && _jsx(EmptyState, { children: "\u672A\u9009\u62E9\u8BDD\u9898" }), topicPath.length !== 0 && cachedMessages.length === 0 && (_jsx(EmptyState, { children: "\u6B63\u5728\u7B49\u5F85\u4E0B\u4E00\u6761\u6D88\u606F\u2026\u2026" })), topicPath.length !== 0 && firstCachedMessage && (_jsx(Stack, { overflow: "auto", className: classes.monospace, children: _jsx(Table, { value: firstCachedMessage.value, accessorPath: "" }) }))] }));
}
TablePanel.panelType = "Table";
TablePanel.defaultConfig = {
    topicPath: "",
};
export default Panel(TablePanel);
