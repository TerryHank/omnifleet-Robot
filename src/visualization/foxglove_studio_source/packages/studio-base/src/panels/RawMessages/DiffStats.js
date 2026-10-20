import { Fragment as _Fragment, jsxs as _jsxs, jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { Typography } from "@mui/material";
import { makeStyles } from "tss-react/mui";
import { diffLabels } from "@foxglove/studio-base/panels/RawMessages/getDiff";
import { getChangeCounts } from "@foxglove/studio-base/panels/RawMessages/utils";
const useStyles = makeStyles()((theme) => ({
    diff: {
        float: "right",
        display: "flex",
        alignItems: "center",
        gap: theme.spacing(0.75),
        marginRight: theme.spacing(0.75),
    },
    badge: {
        display: "inline-flex",
        alignItems: "center",
        gap: theme.spacing(0.25),
        padding: theme.spacing(0, 0.75),
        borderRadius: theme.shape.borderRadius,
        backgroundColor: theme.palette.background.paper,
    },
    changeIndicator: {
        display: "inline-block",
        width: theme.spacing(0.75),
        height: theme.spacing(0.75),
        borderRadius: "50%",
        backgroundColor: theme.palette.warning.main,
    },
}));
export default function DiffStats({ data, itemType, }) {
    const { classes } = useStyles();
    const { ADDED, DELETED, CHANGED, ID } = diffLabels;
    const id = data[ID.labelText];
    const idLabel = id
        ? Object.keys(id)
            .map((key) => `${key}: ${id[key]}`)
            .join(", ")
        : undefined;
    const counts = getChangeCounts(data, {
        [ADDED.labelText]: 0,
        [CHANGED.labelText]: 0,
        [DELETED.labelText]: 0,
    });
    return (_jsxs(_Fragment, { children: [id && (_jsxs(_Fragment, { children: [itemType, " ", idLabel] })), _jsxs("div", { className: classes.diff, children: [(counts[ADDED.labelText] !== 0 || counts[DELETED.labelText] !== 0) && (_jsxs("div", { className: classes.badge, children: [counts[ADDED.labelText] !== 0 && (_jsx(Typography, { variant: "caption", color: "success.main", children: `${diffLabels.ADDED.indicator}${counts[ADDED.labelText]}` })), counts[DELETED.labelText] !== 0 && (_jsx(Typography, { variant: "caption", color: "error.main", children: `${diffLabels.DELETED.indicator}${counts[DELETED.labelText]}` }))] })), counts[CHANGED.labelText] !== 0 && _jsx("div", { className: classes.changeIndicator })] })] }));
}
