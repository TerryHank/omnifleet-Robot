import { jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { useTheme } from "@mui/material";
import { ProgressPlot } from "./ProgressPlot";
export default {
    title: "components/PlaybackControls/ProgressPlot",
    component: ProgressPlot,
    decorators: [
        (Story) => {
            const theme = useTheme();
            return (_jsx("div", { style: {
                    backgroundColor: theme.palette.background.paper,
                    padding: theme.spacing(2),
                    width: "100%",
                    height: "100%",
                }, children: _jsx("div", { style: { backgroundColor: theme.palette.action.focus, height: 40 }, children: _jsx(Story, {}) }) }));
        },
    ],
};
export const DisjointRanges = {
    render: () => (_jsx(ProgressPlot, { loading: false, availableRanges: [
            { start: 0, end: 0.2 },
            { start: 0.8, end: 1 },
        ] })),
    parameters: { colorScheme: "both-column" },
};
export const Loading = {
    render: () => (_jsx(ProgressPlot, { loading: true, availableRanges: [
            { start: 0, end: 0.2 },
            { start: 0.8, end: 1 },
        ] })),
    parameters: { colorScheme: "both-column" },
};
