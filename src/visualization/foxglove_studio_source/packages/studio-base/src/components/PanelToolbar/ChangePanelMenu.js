import { jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { ClickAwayListener, Grow, Paper, Popper } from "@mui/material";
import { useCallback, useContext } from "react";
import { MosaicContext, MosaicWindowContext } from "react-mosaic-component";
import { makeStyles } from "tss-react/mui";
import { PanelCatalog } from "@foxglove/studio-base/components/PanelCatalog";
import PanelContext from "@foxglove/studio-base/components/PanelContext";
import { useCurrentLayoutActions } from "@foxglove/studio-base/context/CurrentLayoutContext";
const useStyles = makeStyles()((theme) => ({
    paper: {
        backgroundColor: theme.palette.background.menu,
        maxHeight: `calc(100vh - ${theme.spacing(12)})`,
        overflow: "auto",
        // Add iOS momentum scrolling for iOS < 13.0
        WebkitOverflowScrolling: "touch",
    },
}));
export default function ChangePanelMenu({ tabId, anchorEl, onClose, }) {
    const { classes } = useStyles();
    const panelContext = useContext(PanelContext);
    const { mosaicActions } = useContext(MosaicContext);
    const { mosaicWindowActions } = useContext(MosaicWindowContext);
    const { swapPanel } = useCurrentLayoutActions();
    const open = Boolean(anchorEl);
    const handleSwap = useCallback((id) => ({ type, config }) => {
        // Reselecting current panel type is a no-op.
        if (type === panelContext?.type) {
            onClose();
            return;
        }
        swapPanel({
            tabId,
            originalId: id ?? "",
            type,
            root: mosaicActions.getRoot(),
            path: mosaicWindowActions.getPath(),
            config: config ?? {},
        });
    }, [onClose, mosaicActions, mosaicWindowActions, panelContext?.type, swapPanel, tabId]);
    // https://github.com/mui/material-ui/issues/35287#issuecomment-1332327752
    const fixMui35287 = {};
    return (_jsx(Popper, { ...fixMui35287, id: "change-panel-menu", open: open, role: undefined, anchorEl: anchorEl, transition: true, placement: "right-start", style: { zIndex: 10000 }, popperOptions: {
            modifiers: [
                {
                    name: "flip",
                    options: { fallbackPlacements: ["right-start", "left-start"] },
                },
            ],
        }, children: ({ TransitionProps, placement }) => (_jsx(Grow, { ...TransitionProps, style: {
                transformOrigin: placement === "right-start" ? "top left" : "top right",
            }, children: _jsx(Paper, { elevation: 8, className: classes.paper, children: _jsx(ClickAwayListener, { onClickAway: onClose, children: _jsx(PanelCatalog, { mode: "list", isMenu: true, selectedPanelType: panelContext?.type, onPanelSelect: handleSwap(panelContext?.id) }) }) }) })) }));
}
