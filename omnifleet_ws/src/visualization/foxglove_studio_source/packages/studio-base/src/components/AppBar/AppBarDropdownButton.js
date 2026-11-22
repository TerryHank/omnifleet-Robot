import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { ChevronDown12Filled } from "@fluentui/react-icons";
import { ButtonBase, Typography } from "@mui/material";
import { forwardRef } from "react";
import tinycolor2 from "tinycolor2";
import { makeStyles } from "tss-react/mui";
import Stack from "@foxglove/studio-base/components/Stack";
import TextMiddleTruncate from "@foxglove/studio-base/components/TextMiddleTruncate";
import { APP_BAR_HEIGHT } from "./constants";
const useStyles = makeStyles()((theme) => ({
    textTruncate: {
        maxWidth: "18vw",
        overflow: "hidden",
    },
    subheader: {
        fontSize: 8,
        opacity: 0.6,
    },
    layoutButton: {
        font: "inherit",
        height: APP_BAR_HEIGHT,
        fontSize: theme.typography.body2.fontSize,
        justifyContent: "space-between",
        minWidth: 120,
        padding: theme.spacing(1.125, 1.5),
        gap: theme.spacing(1.5),
        borderRadius: 0,
        ":hover": {
            backgroundColor: tinycolor2(theme.palette.common.white).setAlpha(0.08).toString(),
        },
        "&.Mui-selected": {
            backgroundColor: theme.palette.appBar.primary,
        },
    },
}));
/**
 * A button that can be used in the app bar to open a dropdown menu.
 */
const AppBarDropdownButton = forwardRef((props, ref) => {
    const { title, subheader, onClick, selected, ...rest } = props;
    const { classes, cx } = useStyles();
    return (_jsxs(ButtonBase, { className: cx(classes.layoutButton, { "Mui-selected": selected }), "aria-haspopup": "true", onClick: onClick, ref: ref, ...rest, children: [_jsxs(Stack, { alignItems: "flex-start", children: [subheader && (_jsx(Typography, { variant: "overline", className: classes.subheader, children: subheader })), _jsx("div", { className: classes.textTruncate, children: _jsx(TextMiddleTruncate, { text: title }) })] }), _jsx(ChevronDown12Filled, {})] }));
});
AppBarDropdownButton.displayName = "AppBarDropdownButton";
// ts-unused-exports:disable-next-line
export { AppBarDropdownButton };
