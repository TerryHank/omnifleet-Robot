import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { ChevronDown12Regular, PanelLeft24Filled, PanelLeft24Regular, PanelRight24Filled, PanelRight24Regular, SlideAdd24Regular, } from "@fluentui/react-icons";
import { Avatar, IconButton, Tooltip } from "@mui/material";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import tc from "tinycolor2";
import { makeStyles } from "tss-react/mui";
import { FoxgloveLogo } from "@foxglove/studio-base/components/FoxgloveLogo";
import Stack from "@foxglove/studio-base/components/Stack";
import { useAppContext } from "@foxglove/studio-base/context/AppContext";
import { useCurrentLayoutSelector, } from "@foxglove/studio-base/context/CurrentLayoutContext";
import { useWorkspaceStore, } from "@foxglove/studio-base/context/Workspace/WorkspaceContext";
import { useWorkspaceActions } from "@foxglove/studio-base/context/Workspace/useWorkspaceActions";
import { AddPanelMenu } from "./AddPanelMenu";
import { AppBarContainer } from "./AppBarContainer";
import { AppBarIconButton } from "./AppBarIconButton";
import { AppMenu } from "./AppMenu";
import { CustomWindowControls } from "./CustomWindowControls";
import { DataSource } from "./DataSource";
import { SettingsMenu } from "./SettingsMenu";
const useStyles = makeStyles()((theme, { debugDragRegion = false }, classes) => {
    const NOT_DRAGGABLE_STYLE = { WebkitAppRegion: "no-drag" };
    if (debugDragRegion) {
        NOT_DRAGGABLE_STYLE.backgroundColor = "red";
    }
    return {
        toolbar: {
            display: "grid",
            width: "100%",
            gridTemplateAreas: `"start middle end"`,
            gridTemplateColumns: "1fr auto 1fr",
            alignItems: "center",
        },
        logo: {
            padding: theme.spacing(0.75, 0.5),
            fontSize: "2rem",
            color: theme.palette.appBar.primary,
            borderRadius: 0,
            "svg:not(.MuiSvgIcon-root)": {
                fontSize: "1em",
            },
            "&:hover": {
                backgroundColor: tc(theme.palette.common.white).setAlpha(0.08).toRgbString(),
            },
            "&.Mui-selected": {
                backgroundColor: theme.palette.appBar.primary,
                color: theme.palette.common.white,
            },
            "&.Mui-disabled": {
                color: "currentColor",
                opacity: theme.palette.action.disabledOpacity,
            },
        },
        dropDownIcon: {
            fontSize: "12px !important",
        },
        start: {
            gridArea: "start",
            display: "flex",
            flex: 1,
            alignItems: "center",
        },
        startInner: {
            display: "flex",
            alignItems: "center",
            ...NOT_DRAGGABLE_STYLE, // make buttons clickable for desktop app
        },
        middle: {
            gridArea: "middle",
            justifySelf: "center",
            overflow: "hidden",
            maxWidth: "100%",
            ...NOT_DRAGGABLE_STYLE, // make buttons clickable for desktop app
        },
        end: {
            gridArea: "end",
            flex: 1,
            display: "flex",
            justifyContent: "flex-end",
        },
        endInner: {
            display: "flex",
            alignItems: "center",
            ...NOT_DRAGGABLE_STYLE, // make buttons clickable for desktop app
        },
        keyEquivalent: {
            fontFamily: theme.typography.fontMonospace,
            background: tc(theme.palette.common.white).darken(45).toString(),
            padding: theme.spacing(0, 0.5),
            aspectRatio: 1,
            borderRadius: theme.shape.borderRadius,
            marginLeft: theme.spacing(1),
        },
        tooltip: {
            marginTop: `${theme.spacing(0.5)} !important`,
        },
        avatar: {
            color: theme.palette.common.white,
            backgroundColor: tc(theme.palette.appBar.main).lighten().toString(),
            height: theme.spacing(3.5),
            width: theme.spacing(3.5),
        },
        iconButton: {
            padding: theme.spacing(1),
            borderRadius: 0,
            "&:hover": {
                backgroundColor: tc(theme.palette.common.white).setAlpha(0.08).toString(),
                [`.${classes.avatar}`]: {
                    backgroundColor: tc(theme.palette.appBar.main).lighten(20).toString(),
                },
            },
            "&.Mui-selected": {
                backgroundColor: theme.palette.appBar.primary,
                [`.${classes.avatar}`]: {
                    backgroundColor: tc(theme.palette.appBar.main).setAlpha(0.3).toString(),
                },
            },
        },
    };
});
const selectHasCurrentLayout = (state) => state.selectedLayout != undefined;
const selectLeftSidebarOpen = (store) => store.sidebars.left.open;
const selectRightSidebarOpen = (store) => store.sidebars.right.open;
export function AppBar(props) {
    const { debugDragRegion, isMaximized, leftInset, onCloseWindow, onDoubleClick, onMaximizeWindow, onMinimizeWindow, onUnmaximizeWindow, showCustomWindowControls = false, } = props;
    const { classes, cx, theme } = useStyles({ debugDragRegion });
    const { t } = useTranslation("appBar");
    const { appBarLayoutButton } = useAppContext();
    const hasCurrentLayout = useCurrentLayoutSelector(selectHasCurrentLayout);
    const leftSidebarOpen = useWorkspaceStore(selectLeftSidebarOpen);
    const rightSidebarOpen = useWorkspaceStore(selectRightSidebarOpen);
    const { sidebarActions } = useWorkspaceActions();
    const [appMenuEl, setAppMenuEl] = useState(undefined);
    const [userAnchorEl, setUserAnchorEl] = useState(undefined);
    const [panelAnchorEl, setPanelAnchorEl] = useState(undefined);
    const appMenuOpen = Boolean(appMenuEl);
    const userMenuOpen = Boolean(userAnchorEl);
    const panelMenuOpen = Boolean(panelAnchorEl);
    return (_jsxs(_Fragment, { children: [_jsx(AppBarContainer, { onDoubleClick: onDoubleClick, leftInset: leftInset, children: _jsxs("div", { className: classes.toolbar, children: [_jsx("div", { className: classes.start, children: _jsxs("div", { className: classes.startInner, children: [_jsxs(IconButton, { className: cx(classes.logo, { "Mui-selected": appMenuOpen }), color: "inherit", id: "app-menu-button", title: "\u83DC\u5355", "aria-controls": appMenuOpen ? "app-menu" : undefined, "aria-haspopup": "true", "aria-expanded": appMenuOpen ? "true" : undefined, "data-tourid": "app-menu-button", onClick: (event) => {
                                            setAppMenuEl(event.currentTarget);
                                        }, children: [_jsx(FoxgloveLogo, { fontSize: "inherit", color: "inherit" }), _jsx(ChevronDown12Regular, { className: classes.dropDownIcon, primaryFill: theme.palette.common.white })] }), _jsx(AppMenu, { open: appMenuOpen, anchorEl: appMenuEl, handleClose: () => {
                                            setAppMenuEl(undefined);
                                        } }), _jsx(AppBarIconButton, { className: cx({ "Mui-selected": panelMenuOpen }), color: "inherit", disabled: !hasCurrentLayout, id: "add-panel-button", "data-tourid": "add-panel-button", title: t("addPanel"), "aria-label": "\u6DFB\u52A0\u9762\u677F\u6309\u94AE", "aria-controls": panelMenuOpen ? "add-panel-menu" : undefined, "aria-haspopup": "true", "aria-expanded": panelMenuOpen ? "true" : undefined, onClick: (event) => {
                                            setPanelAnchorEl(event.currentTarget);
                                        }, children: _jsx(SlideAdd24Regular, {}) })] }) }), _jsx("div", { className: classes.middle, children: _jsx(DataSource, {}) }), _jsx("div", { className: classes.end, children: _jsxs("div", { className: classes.endInner, children: [appBarLayoutButton, _jsxs(Stack, { direction: "row", alignItems: "center", "data-tourid": "sidebar-button-group", children: [_jsx(AppBarIconButton, { title: _jsxs(_Fragment, { children: [leftSidebarOpen ? t("hideLeftSidebar") : t("showLeftSidebar"), " ", _jsx("kbd", { className: classes.keyEquivalent, children: "[" })] }), "aria-label": `${leftSidebarOpen ? t("hideLeftSidebar") : t("showLeftSidebar")}`, onClick: () => {
                                                    sidebarActions.left.setOpen(!leftSidebarOpen);
                                                }, "data-tourid": "left-sidebar-button", children: leftSidebarOpen ? _jsx(PanelLeft24Filled, {}) : _jsx(PanelLeft24Regular, {}) }), _jsx(AppBarIconButton, { title: _jsxs(_Fragment, { children: [rightSidebarOpen ? t("hideRightSidebar") : t("showRightSidebar"), " ", _jsx("kbd", { className: classes.keyEquivalent, children: "]" })] }), "aria-label": `${rightSidebarOpen ? t("hideRightSidebar") : t("showRightSidebar")}`, onClick: () => {
                                                    sidebarActions.right.setOpen(!rightSidebarOpen);
                                                }, "data-tourid": "right-sidebar-button", children: rightSidebarOpen ? _jsx(PanelRight24Filled, {}) : _jsx(PanelRight24Regular, {}) })] }), _jsx(Tooltip, { classes: { tooltip: classes.tooltip }, title: "\u7528\u6237\u8D44\u6599", arrow: false, children: _jsx(IconButton, { className: cx(classes.iconButton, { "Mui-selected": userMenuOpen }), "aria-label": "\u7528\u6237\u8D44\u6599\u83DC\u5355\u6309\u94AE", color: "inherit", id: "user-button", "data-tourid": "user-button", "aria-controls": userMenuOpen ? "user-menu" : undefined, "aria-haspopup": "true", "aria-expanded": userMenuOpen ? "true" : undefined, onClick: (event) => {
                                                setUserAnchorEl(event.currentTarget);
                                            }, "data-testid": "user-button", children: _jsx(Avatar, { className: classes.avatar, variant: "rounded" }) }) }), showCustomWindowControls && (_jsx(CustomWindowControls, { onMinimizeWindow: onMinimizeWindow, isMaximized: isMaximized, onUnmaximizeWindow: onUnmaximizeWindow, onMaximizeWindow: onMaximizeWindow, onCloseWindow: onCloseWindow }))] }) })] }) }), _jsx(AddPanelMenu, { anchorEl: panelAnchorEl, open: panelMenuOpen, handleClose: () => {
                    setPanelAnchorEl(undefined);
                } }), _jsx(SettingsMenu, { anchorEl: userAnchorEl, open: userMenuOpen, handleClose: () => {
                    setUserAnchorEl(undefined);
                } })] }));
}
