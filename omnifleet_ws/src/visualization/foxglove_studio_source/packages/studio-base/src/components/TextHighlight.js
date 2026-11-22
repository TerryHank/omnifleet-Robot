import { Fragment as _Fragment, jsx as _jsx } from "react/jsx-runtime";
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
import fuzzySort from "fuzzysort";
import { makeStyles } from "tss-react/mui";
const useStyles = makeStyles()((theme) => ({
    root: {
        ".TextHighlight-highlight": {
            color: theme.palette.primary.main,
            fontWeight: "bold",
        },
    },
}));
export default function TextHighlight({ targetStr = "", searchText = "" }) {
    const { classes } = useStyles();
    if (searchText.length === 0) {
        return _jsx(_Fragment, { children: targetStr });
    }
    const match = fuzzySort.single(searchText, targetStr);
    const result = match
        ? fuzzySort.highlight(match, "<span class='TextHighlight-highlight'>", "</span>")
        : undefined;
    return (_jsx("span", { className: classes.root, children: result != undefined && result.length > 0 ? (_jsx("span", { dangerouslySetInnerHTML: { __html: result } })) : (targetStr) }));
}
