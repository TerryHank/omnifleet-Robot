import { jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { CheckmarkCircle20Regular, DismissCircle20Regular, Dismiss16Filled, Info20Regular, Warning20Regular, } from "@fluentui/react-icons";
import { Grow, IconButton } from "@mui/material";
import { SnackbarProvider, useSnackbar, MaterialDesignContent, } from "notistack";
import { forwardRef } from "react";
import { makeStyles } from "tss-react/mui";
import { APP_BAR_HEIGHT } from "@foxglove/studio-base/components/AppBar/constants";
const anchorWithOffset = (origin) => ({
    "&.notistack-SnackbarContainer": {
        top: origin === "top" ? APP_BAR_HEIGHT : undefined,
    },
});
const useStyles = makeStyles()((theme, _params, classes) => ({
    icon: {},
    dismissButton: {
        color: theme.palette.common.white,
        "svg:not(.MuiSvgIcon-root)": {
            fontSize: 16,
        },
    },
    root: {
        "#notistack-snackbar": {
            padding: 0,
            gap: theme.spacing(0.75),
        },
        "&.notistack-MuiContent": {
            padding: theme.spacing(0.5, 1.5, 0.5, 1),
            fontSize: theme.typography.body2.fontSize,
        },
        "&.notistack-MuiContent-default": {
            backgroundColor: theme.palette.background.paper,
            color: theme.palette.text.primary,
            [`.${classes.icon}`]: { color: theme.palette.primary.main },
            [`.${classes.dismissButton}`]: { color: theme.palette.text.primary },
        },
        "&.notistack-MuiContent-success": {
            backgroundColor: theme.palette.success.main,
        },
        "&.notistack-MuiContent-error": {
            backgroundColor: theme.palette.error.main,
        },
        "&.notistack-MuiContent-info": {
            backgroundColor: theme.palette.info.main,
        },
        "&.notistack-MuiContent-warning": {
            backgroundColor: theme.palette.warning.main,
        },
    },
}));
const useContainerStyles = makeStyles()({
    /* eslint-disable tss-unused-classes/unused-classes */
    containerAnchorOriginBottomCenter: anchorWithOffset("bottom"),
    containerAnchorOriginBottomRight: anchorWithOffset("bottom"),
    containerAnchorOriginBottomLeft: anchorWithOffset("bottom"),
    containerAnchorOriginTopCenter: anchorWithOffset("top"),
    containerAnchorOriginTopRight: anchorWithOffset("top"),
    containerAnchorOriginTopLeft: anchorWithOffset("top"),
    /* eslint-enable tss-unused-classes/unused-classes */
});
const CloseSnackbarAction = ({ id }) => {
    const { closeSnackbar } = useSnackbar();
    const { classes } = useStyles();
    return (_jsx(IconButton, { size: "small", className: classes.dismissButton, onClick: () => {
            closeSnackbar(id);
        }, children: _jsx(Dismiss16Filled, {}) }));
};
const Snackbar = forwardRef((props, ref) => {
    const { classes } = useStyles();
    return _jsx(MaterialDesignContent, { ref: ref, ...props, className: classes.root });
});
Snackbar.displayName = "Snackbar";
export default function StudioToastProvider({ children }) {
    const { classes: containerClasses } = useContainerStyles();
    const { classes } = useStyles();
    return (_jsx(SnackbarProvider, { Components: {
            default: Snackbar,
            error: Snackbar,
            success: Snackbar,
            warning: Snackbar,
            info: Snackbar,
        }, action: (id) => _jsx(CloseSnackbarAction, { id: id }), iconVariant: {
            default: _jsx(Info20Regular, { className: classes.icon }),
            info: _jsx(Info20Regular, { className: classes.icon }),
            error: _jsx(DismissCircle20Regular, { className: classes.icon }),
            warning: _jsx(Warning20Regular, { className: classes.icon }),
            success: _jsx(CheckmarkCircle20Regular, { className: classes.icon }),
        }, anchorOrigin: {
            vertical: "top",
            horizontal: "center",
        }, maxSnack: 5, preventDuplicate: true, TransitionComponent: Grow, classes: containerClasses, children: children }));
}
