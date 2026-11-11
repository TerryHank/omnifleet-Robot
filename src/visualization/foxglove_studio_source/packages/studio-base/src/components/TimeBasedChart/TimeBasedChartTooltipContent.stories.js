import { jsx as _jsx } from "react/jsx-runtime";
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
import { Tooltip } from "@mui/material";
import TimeBasedChartTooltipContent from "./TimeBasedChartTooltipContent";
export default {
    title: "components/TimeBasedChart/TimeBasedChartTooltipContent",
    component: TimeBasedChartTooltipContent,
};
export const SingleItemSingleDataset = {
    render: function Story() {
        const data = {
            configIndex: 0,
            value: 3,
            constantName: "ACTIVE",
        };
        return (_jsx(Tooltip, { open: true, title: _jsx(TimeBasedChartTooltipContent, { multiDataset: false, content: [data] }), placement: "top", arrow: true, PopperProps: {
                anchorEl: {
                    getBoundingClientRect: () => {
                        return new DOMRect(200, 100, 0, 0);
                    },
                },
            }, children: _jsx("div", { style: { width: "100%", height: "100%" } }) }));
    },
    parameters: { colorScheme: "dark" },
};
export const SingleItemSingleDatasetLight = {
    ...SingleItemSingleDataset,
    parameters: { colorScheme: "light" },
};
export const SingleItemMultiDataset = {
    render: function Story() {
        const data = {
            configIndex: 0,
            value: 3,
            constantName: "ACTIVE",
        };
        return (_jsx(Tooltip, { open: true, title: _jsx(TimeBasedChartTooltipContent, { multiDataset: true, content: [data], labelsByConfigIndex: { "0": "/some/topic.path", "1": "Series B" } }), placement: "top", arrow: true, PopperProps: {
                anchorEl: {
                    getBoundingClientRect: () => {
                        return new DOMRect(200, 100, 0, 0);
                    },
                },
            }, children: _jsx("div", { style: { width: "100%", height: "100%" } }) }));
    },
    parameters: { colorScheme: "dark" },
};
export const SingleItemMultiDatasetLight = {
    ...SingleItemMultiDataset,
    parameters: { colorScheme: "light" },
};
export const MultipleItemsSingleDataset = {
    render: function Story() {
        const data = {
            configIndex: 0,
            value: 3,
            constantName: "ACTIVE",
        };
        return (_jsx(Tooltip, { open: true, title: _jsx(TimeBasedChartTooltipContent, { multiDataset: false, content: [data, data] }), placement: "top", arrow: true, PopperProps: {
                anchorEl: {
                    getBoundingClientRect: () => {
                        return new DOMRect(200, 100, 0, 0);
                    },
                },
            }, children: _jsx("div", { style: { width: "100%", height: "100%" } }) }));
    },
    parameters: { colorScheme: "dark" },
};
export const MultipleItemsSingleDatasetLight = {
    ...MultipleItemsSingleDataset,
    parameters: { colorScheme: "light" },
};
export const MultipleItemsMultipleDataset = {
    render: function Story() {
        const data = [
            {
                configIndex: 0,
                value: 3,
                constantName: "ACTIVE",
            },
            {
                configIndex: 1,
                value: 4,
                constantName: "ACTIVE",
            },
        ];
        return (_jsx(Tooltip, { open: true, title: _jsx(TimeBasedChartTooltipContent, { multiDataset: true, content: data, colorsByConfigIndex: { "0": "chartreuse", "1": "yellow" }, labelsByConfigIndex: { "0": "Series A", "1": "Series B" } }), placement: "top", arrow: true, PopperProps: {
                anchorEl: {
                    getBoundingClientRect: () => {
                        return new DOMRect(200, 100, 0, 0);
                    },
                },
            }, children: _jsx("div", { style: { width: "100%", height: "100%" } }) }));
    },
    parameters: { colorScheme: "dark" },
};
export const MultipleItemsMultiDatasetLight = {
    ...MultipleItemsMultipleDataset,
    parameters: { colorScheme: "light" },
};
