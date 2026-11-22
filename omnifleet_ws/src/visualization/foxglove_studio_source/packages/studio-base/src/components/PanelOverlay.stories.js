import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { Delete20Regular, TabDesktop20Regular, TabDesktopMultiple20Regular, TableSimple20Regular, } from "@fluentui/react-icons";
import Stack from "@foxglove/studio-base/components/Stack";
import { PanelOverlay } from "./PanelOverlay";
export default {
    title: "components/PanelOverlay",
    component: PanelOverlay,
    decorators: [],
    render: (args) => {
        return (_jsxs(Stack, { flex: "auto", position: "relative", justifyContent: "center", alignItems: "center", paddingTop: 3.75, children: [_jsx(PanelOverlay, { ...args }), "Background content"] }));
    },
};
export const Default = {};
export const ValidDropTarget = {
    args: {
        open: true,
        variant: "validDropTarget",
        dropMessage: "View /topic_name/field_name",
    },
};
export const InvalidDropTarget = {
    args: {
        open: true,
        variant: "invalidDropTarget",
        dropMessage: "View /topic_name/field_name",
    },
};
export const SelectedPanelActions = {
    args: {
        open: true,
        variant: "selected",
        actions: [
            { key: "group", text: "Group in tab", icon: _jsx(TabDesktop20Regular, {}) },
            { key: "create-tabs", text: "Create tabs", icon: _jsx(TabDesktopMultiple20Regular, {}) },
        ],
    },
    parameters: {
        colorScheme: "both-column",
    },
    decorators: [
        (Story) => (_jsxs(Stack, { fullHeight: true, gap: 1, children: [_jsx(Story, {}), _jsxs("div", { style: {
                        height: "100%",
                        display: "grid",
                        gridTemplateColumns: "1fr 260px 100px",
                        gap: 8,
                    }, children: [_jsx(Story, {}), _jsx(Story, {}), _jsx(Story, {})] })] })),
    ],
};
export const QuickActions = {
    args: {
        open: true,
        variant: "selected",
        actions: [
            { key: "split", text: "Split panel", icon: _jsx(TableSimple20Regular, {}) },
            { key: "remove", text: "Remove panel", icon: _jsx(Delete20Regular, {}), color: "error" },
        ],
    },
    parameters: {
        colorScheme: "both-column",
    },
    decorators: [
        (Story) => (_jsxs(Stack, { fullHeight: true, gap: 1, children: [_jsx(Story, {}), _jsxs("div", { style: {
                        height: "100%",
                        display: "grid",
                        gridTemplateColumns: "1fr 260px auto",
                        gap: 8,
                    }, children: [_jsx(Story, {}), _jsx(Story, {}), _jsx(Story, {})] })] })),
    ],
};
