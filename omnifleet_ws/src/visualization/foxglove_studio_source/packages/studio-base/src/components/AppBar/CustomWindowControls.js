import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import CheckBoxOutlineBlankIcon from "@mui/icons-material/CheckBoxOutlineBlank";
import CloseIcon from "@mui/icons-material/Close";
import FilterNoneIcon from "@mui/icons-material/FilterNone";
import MinimizeIcon from "@mui/icons-material/Minimize";
import { IconButton } from "@mui/material";
import { makeStyles } from "tss-react/mui";
import Stack from "@foxglove/studio-base/components/Stack";
const useStyles = makeStyles()((theme) => ({
    closeButton: {
        ":hover": {
            backgroundColor: theme.palette.error.main,
        },
    },
}));
export function CustomWindowControls({ isMaximized = false, onMinimizeWindow, onMaximizeWindow, onUnmaximizeWindow, onCloseWindow, }) {
    const { classes } = useStyles();
    return (_jsxs(Stack, { direction: "row", gap: 1, paddingX: 1, children: [_jsx(IconButton, { size: "small", color: "inherit", onClick: onMinimizeWindow, "data-testid": "win-minimize", children: _jsx(MinimizeIcon, { fontSize: "inherit", color: "inherit" }) }), _jsx(IconButton, { size: "small", color: "inherit", onClick: isMaximized ? onUnmaximizeWindow : onMaximizeWindow, "data-testid": "win-maximize", children: isMaximized ? (_jsx(FilterNoneIcon, { fontSize: "inherit", color: "inherit" })) : (_jsx(CheckBoxOutlineBlankIcon, { fontSize: "inherit", color: "inherit" })) }), _jsx(IconButton, { className: classes.closeButton, size: "small", color: "inherit", onClick: onCloseWindow, "data-testid": "win-close", children: _jsx(CloseIcon, { fontSize: "inherit", color: "inherit" }) })] }));
}
