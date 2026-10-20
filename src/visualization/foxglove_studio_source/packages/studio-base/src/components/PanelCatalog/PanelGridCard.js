import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { Card, CardActionArea, CardContent, CardMedia, Typography } from "@mui/material";
import { useCallback } from "react";
import { makeStyles } from "tss-react/mui";
import Stack from "@foxglove/studio-base/components/Stack";
import TextHighlight from "@foxglove/studio-base/components/TextHighlight";
const useStyles = makeStyles()((theme) => {
    return {
        fullHeight: {
            height: "100%",
        },
        imagePlaceholder: {
            paddingBottom: `${(200 / 280) * 100}%`,
            backgroundColor: theme.palette.background.default,
        },
        cardContent: {
            flex: "auto",
        },
    };
});
export function PanelGridCard(props) {
    const { searchQuery, panel, onClick } = props;
    const { classes } = useStyles();
    const targetString = panel.extensionNamespace
        ? `${panel.title} [${panel.extensionNamespace}]`
        : panel.title;
    const onClickWithStopPropagation = useCallback((event) => {
        event.stopPropagation();
        onClick();
    }, [onClick]);
    return (_jsx(Card, { className: classes.fullHeight, children: _jsx(CardActionArea, { onClick: onClickWithStopPropagation, className: classes.fullHeight, children: _jsxs(Stack, { fullHeight: true, children: [panel.thumbnail != undefined ? (_jsx(CardMedia, { component: "img", image: panel.thumbnail, alt: panel.title })) : (_jsx("div", { className: classes.imagePlaceholder })), _jsxs(CardContent, { className: classes.cardContent, children: [_jsx(Typography, { variant: "subtitle2", gutterBottom: true, children: _jsx("span", { "data-testid": `panel-grid-card ${panel.title}`, children: _jsx(TextHighlight, { targetStr: targetString, searchText: searchQuery }) }) }), _jsx(Typography, { variant: "body2", color: "text.secondary", children: _jsx(TextHighlight, { targetStr: panel.description ?? "", searchText: searchQuery }) })] })] }) }) }));
}
