import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
//
// This file incorporates work covered by the following copyright and
// permission notice:
//
//   Copyright 2019-2021 Cruise LLC
//
//   This source code is licensed under the Apache License, Version 2.0,
//   found at http://www.apache.org/licenses/LICENSE-2.0
//   You may not use this file except in compliance with the License.
import { Link, Typography } from "@mui/material";
import { useCallback } from "react";
import { useDrop } from "react-dnd";
import { useTranslation } from "react-i18next";
import { MosaicDragType } from "react-mosaic-component";
import { makeStyles } from "tss-react/mui";
import { PanelCatalog } from "@foxglove/studio-base/components/PanelCatalog";
import Stack from "@foxglove/studio-base/components/Stack";
import { useCurrentLayoutActions } from "@foxglove/studio-base/context/CurrentLayoutContext";
import { getPanelIdForType } from "@foxglove/studio-base/util/layout";
const useStyles = makeStyles()((theme) => ({
    root: {
        backgroundColor: theme.palette.background.paper,
        width: "100%",
        height: "100%",
        overflowY: "auto",
    },
    dropTarget: {
        width: "100%",
        height: "100%",
        minHeight: 0,
    },
    isOver: {
        "&:after": {
            content: "''",
            borderColor: `1px solid ${theme.palette.action.selected}`,
            backgroundColor: theme.palette.action.focus,
            position: "absolute",
            top: 0,
            right: 0,
            left: 0,
            bottom: 0,
            zIndex: theme.zIndex.appBar,
        },
    },
}));
export const EmptyPanelLayout = ({ tabId }) => {
    const { classes, cx } = useStyles();
    const { addPanel } = useCurrentLayoutActions();
    const { t } = useTranslation("addPanel");
    const [{ isOver }, drop] = useDrop({
        accept: MosaicDragType.WINDOW,
        drop: () => {
            return { tabId };
        },
        collect: (monitor) => ({
            isOver: monitor.isOver(),
        }),
    });
    const onPanelSelect = useCallback(({ type, config }) => {
        const id = getPanelIdForType(type);
        addPanel({ tabId, id, config });
    }, [addPanel, tabId]);
    return (_jsx("div", { ref: drop, "data-testid": "empty-drop-target", className: cx(classes.dropTarget, { [classes.isOver]: isOver }), children: _jsx("div", { className: classes.root, children: _jsxs(Stack, { paddingBottom: 2, children: [_jsxs(Typography, { variant: "body2", paddingX: 2, paddingTop: 2, children: [t("selectPanelToAddToLayout"), " ", _jsx(Link, { color: "primary", target: "_blank", href: "https://docs.foxglove.dev/docs/visualization/layouts", children: t("learnMore", { ns: "general" }) })] }), _jsx(PanelCatalog, { mode: "grid", onPanelSelect: onPanelSelect })] }) }) }));
};
