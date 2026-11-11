import { jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { Typography } from "@mui/material";
import { makeStyles } from "tss-react/mui";
import Stack from "@foxglove/studio-base/components/Stack";
const useStyles = makeStyles()((theme) => ({
    root: {
        whiteSpace: "pre-line",
        code: {
            color: theme.palette.primary.main,
            background: "transparent",
            padding: 0,
        },
    },
}));
export default function EmptyState({ children, className, }) {
    const { classes, cx } = useStyles();
    return (_jsx(Stack, { className: cx(classes.root, className), flex: "auto", alignItems: "center", justifyContent: "center", fullHeight: true, paddingX: 1, children: _jsx(Typography, { variant: "body2", color: "text.secondary", lineHeight: 1.4, align: "center", children: children }) }));
}
