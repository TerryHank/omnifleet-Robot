import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { useTheme } from "@mui/material";
import Stack from "./Stack";
export default {
    component: Stack,
    title: "components/Stack",
};
const ITEMS = new Array(3).fill({});
function Box({ children }) {
    const theme = useTheme();
    return (_jsx(Stack, { alignItems: "center", justifyContent: "center", padding: 1, fullHeight: true, style: {
            textAlign: "center",
            border: `1px solid ${theme.palette.divider}`,
            backgroundColor: theme.palette.action.hover,
        }, children: children }));
}
export const Default = {
    render: () => {
        return (_jsxs(Stack, { "data-testid": true, padding: 2, gap: 2, fullHeight: true, children: [_jsx(Stack, { direction: "row", gap: 2, children: ITEMS.map((_, index) => (_jsx(Stack, { flex: "auto", children: _jsx(Box, { children: `Row item ${index + 1}` }) }, index))) }), _jsxs(Stack, { flexGrow: 2, justifyContent: "space-between", gap: 2, children: [_jsx(Stack, { direction: "row", gap: 2, justifyContent: "flex-start", children: ITEMS.map((_, index) => (_jsx(Box, { children: `Row item ${index + 1}` }, index))) }), _jsx(Stack, { direction: "row", justifyContent: "center", gap: 2, alignSelf: "center", children: ITEMS.map((_, index) => (_jsx(Box, { children: `Row item ${index + 1}` }, index))) }), _jsx(Stack, { direction: "row", justifyContent: "flex-end", gap: 2, alignSelf: "flex-end", children: ITEMS.map((_, index) => (_jsx(Box, { children: `Row item ${index + 1}` }, index))) })] }), _jsx(Stack, { gap: 2, justifyContent: "space-between", children: ITEMS.map((_, index) => (_jsx(Stack, { flex: "auto", children: _jsx(Box, { children: `Col item ${index + 1}` }) }, index))) }), _jsxs(Stack, { flex: "auto", gap: 2, justifyContent: "space-between", children: [_jsx(Stack, { gap: 2, alignSelf: "flex-start", children: ITEMS.map((_, index) => (_jsx(Box, { children: `Col item ${index + 1}` }, index))) }), _jsx(Stack, { gap: 2, alignSelf: "center", children: ITEMS.map((_, index) => (_jsx(Box, { children: `Col item ${index + 1}` }, index))) }), _jsx(Stack, { gap: 2, alignSelf: "flex-end", children: ITEMS.map((_, index) => (_jsx(Box, { children: `Col item ${index + 1}` }, index))) })] })] }));
    },
};
