import { jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// fil
import { Container } from "@mui/material";
import { useCallback } from "react";
import { makeStyles } from "tss-react/mui";
import { PanelGridCard } from "./PanelGridCard";
const useStyles = makeStyles()((theme) => ({
    grid: {
        display: "grid !important",
        gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))",
        gap: theme.spacing(2),
    },
}));
export function PanelGrid(props) {
    const { filteredPanels, onPanelSelect, searchQuery = "" } = props;
    const { classes } = useStyles();
    const displayPanelListItem = useCallback((panelInfo) => {
        const { title, type, config } = panelInfo;
        return (_jsx(PanelGridCard, { panel: panelInfo, searchQuery: searchQuery, onClick: () => {
                onPanelSelect({ type, config });
            } }, `${type}-${title}`));
    }, [onPanelSelect, searchQuery]);
    return (_jsx(Container, { className: classes.grid, maxWidth: false, children: filteredPanels.map(displayPanelListItem) }));
}
