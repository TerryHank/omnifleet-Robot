import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import CloseIcon from "@mui/icons-material/Close";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import { Alert, Button, Checkbox, Dialog, DialogActions, DialogTitle, FormControlLabel, FormLabel, IconButton, Link, Tab, Tabs, Typography, useMediaQuery, } from "@mui/material";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { makeStyles } from "tss-react/mui";
import { AppSetting } from "@foxglove/studio-base";
import OsContextSingleton from "@foxglove/studio-base/OsContextSingleton";
import CopyButton from "@foxglove/studio-base/components/CopyButton";
import { ExperimentalFeatureSettings } from "@foxglove/studio-base/components/ExperimentalFeatureSettings";
import FoxgloveLogoText from "@foxglove/studio-base/components/FoxgloveLogoText";
import Stack from "@foxglove/studio-base/components/Stack";
import { useAppContext } from "@foxglove/studio-base/context/AppContext";
import { useWorkspaceStore, } from "@foxglove/studio-base/context/Workspace/WorkspaceContext";
import { useAppConfigurationValue } from "@foxglove/studio-base/hooks";
import isDesktopApp from "@foxglove/studio-base/util/isDesktopApp";
import { AutoUpdate, ColorSchemeSettings, LanguageSettings, LaunchDefault, MessageFramerate, RosPackagePath, TimeFormat, TimezoneSettings, } from "./settings";
const useStyles = makeStyles()((theme) => ({
    layoutGrid: {
        display: "grid",
        gap: theme.spacing(2),
        height: "70vh",
        paddingLeft: theme.spacing(1),
        overflowY: "hidden",
        [theme.breakpoints.up("sm")]: {
            gridTemplateColumns: "auto minmax(0, 1fr)",
        },
    },
    logo: {
        width: 212,
        height: "auto",
        marginLeft: theme.spacing(-1),
    },
    tabPanel: {
        display: "none",
        marginRight: "-100%",
        width: "100%",
        padding: theme.spacing(0, 4, 4),
    },
    tabPanelActive: {
        display: "block",
    },
    checkbox: {
        "&.MuiCheckbox-root": {
            paddingTop: 0,
        },
    },
    dialogActions: {
        position: "sticky",
        backgroundColor: theme.palette.background.paper,
        borderTop: `${theme.palette.divider} 1px solid`,
        padding: theme.spacing(1),
        bottom: 0,
    },
    formControlLabel: {
        "&.MuiFormControlLabel-root": {
            alignItems: "start",
        },
    },
    tab: {
        svg: {
            fontSize: "inherit",
        },
        "> span, > .MuiSvgIcon-root": {
            display: "flex",
            color: theme.palette.primary.main,
            marginRight: theme.spacing(1.5),
            height: theme.typography.pxToRem(21),
            width: theme.typography.pxToRem(21),
        },
        [theme.breakpoints.up("sm")]: {
            textAlign: "right",
            flexDirection: "row",
            justifyContent: "flex-start",
            alignItems: "center",
            minHeight: "auto",
            paddingTop: theme.spacing(1.5),
            paddingBottom: theme.spacing(1.5),
        },
    },
    indicator: {
        [theme.breakpoints.up("sm")]: {
            right: 0,
            width: "100%",
            backgroundColor: theme.palette.action.hover,
            borderRadius: theme.shape.borderRadius,
        },
    },
    dialogTitle: {
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        fontSize: theme.typography.h3.fontSize,
    },
}));
const aboutItems = new Map([
    [
        "resources",
        {
            subheader: "External resources",
            links: [
                ...(isDesktopApp() ? [] : [{ title: "Desktop app", url: "https://foxglove.dev/download" }]),
                { title: "Browse docs", url: "https://docs.foxglove.dev/docs" },
                { title: "Join our community", url: "https://foxglove.dev/community" },
            ],
        },
    ],
    [
        "products",
        {
            subheader: "Products",
            links: [
                { title: "Foxglove Studio", url: "https://foxglove.dev/studio" },
                { title: "Foxglove Data Platform", url: "https://foxglove.dev/data-platform" },
            ],
        },
    ],
    [
        "contact",
        {
            subheader: "Contact",
            links: [
                { title: "Give feedback", url: "https://foxglove.dev/contact" },
                { title: "Schedule a demo", url: "https://foxglove.dev/demo" },
            ],
        },
    ],
    [
        "legal",
        {
            subheader: "Legal",
            links: [
                { title: "License terms", url: "https://foxglove.dev/legal/studio-license" },
                { title: "Privacy policy", url: "https://foxglove.dev/legal/privacy" },
            ],
        },
    ],
]);
const selectWorkspaceInitialActiveTab = (store) => store.dialogs.preferences.initialTab;
export function AppSettingsDialog(props) {
    const { t } = useTranslation("appSettings");
    const { activeTab: _activeTab } = props;
    const initialActiveTab = useWorkspaceStore(selectWorkspaceInitialActiveTab);
    const [activeTab, setActiveTab] = useState(_activeTab ?? initialActiveTab ?? "general");
    const [debugModeEnabled = false, setDebugModeEnabled] = useAppConfigurationValue(AppSetting.SHOW_DEBUG_PANELS);
    const { classes, cx, theme } = useStyles();
    const smUp = useMediaQuery(theme.breakpoints.up("sm"));
    const { extensionSettings } = useAppContext();
    // automatic updates are a desktop-only setting
    //
    // electron-updater does not provide a way to detect if we are on a supported update platform
    // so we hard-code linux as an _unsupported_ auto-update platform since we cannot auto-update
    // with our .deb package install method on linux.
    const supportsAppUpdates = isDesktopApp() && OsContextSingleton?.platform !== "linux";
    const handleTabChange = (_event, newValue) => {
        setActiveTab(newValue);
    };
    const handleClose = (event) => {
        if (props.onClose != undefined) {
            props.onClose(event, "backdropClick");
        }
    };
    return (_jsxs(Dialog, { ...props, fullWidth: true, maxWidth: "md", "data-testid": `AppSettingsDialog--${activeTab}`, children: [_jsxs(DialogTitle, { className: classes.dialogTitle, children: [t("settings"), _jsx(IconButton, { edge: "end", onClick: handleClose, children: _jsx(CloseIcon, {}) })] }), _jsxs("div", { className: classes.layoutGrid, children: [_jsxs(Tabs, { classes: { indicator: classes.indicator }, value: activeTab, orientation: smUp ? "vertical" : "horizontal", onChange: handleTabChange, children: [_jsx(Tab, { className: classes.tab, label: t("general"), value: "general" }), extensionSettings && (_jsx(Tab, { className: classes.tab, label: t("extensions"), value: "extensions" })), _jsx(Tab, { className: classes.tab, label: t("experimentalFeatures"), value: "experimental-features" }), _jsx(Tab, { className: classes.tab, label: t("about"), value: "about" })] }), _jsxs(Stack, { direction: "row", fullHeight: true, overflowY: "auto", children: [_jsx("section", { className: cx(classes.tabPanel, {
                                    [classes.tabPanelActive]: activeTab === "general",
                                }), children: _jsxs(Stack, { gap: 2, children: [_jsx(ColorSchemeSettings, {}), _jsx(TimezoneSettings, {}), _jsx(TimeFormat, { orientation: smUp ? "horizontal" : "vertical" }), _jsx(MessageFramerate, {}), _jsx(LanguageSettings, {}), supportsAppUpdates && _jsx(AutoUpdate, {}), !isDesktopApp() && _jsx(LaunchDefault, {}), isDesktopApp() && _jsx(RosPackagePath, {}), _jsxs(Stack, { children: [_jsxs(FormLabel, { children: [t("advanced"), ":"] }), _jsx(FormControlLabel, { className: classes.formControlLabel, control: _jsx(Checkbox, { className: classes.checkbox, checked: debugModeEnabled, onChange: (_, checked) => {
                                                            void setDebugModeEnabled(checked);
                                                        } }), label: t("debugModeDescription") })] })] }) }), extensionSettings && (_jsx("section", { className: cx(classes.tabPanel, {
                                    [classes.tabPanelActive]: activeTab === "extensions",
                                }), children: _jsx(Stack, { gap: 2, children: extensionSettings }) })), _jsx("section", { className: cx(classes.tabPanel, {
                                    [classes.tabPanelActive]: activeTab === "experimental-features",
                                }), children: _jsxs(Stack, { gap: 2, children: [_jsx(Alert, { color: "warning", icon: _jsx(WarningAmberIcon, {}), children: t("experimentalFeaturesDescription") }), _jsx(Stack, { paddingLeft: 2, children: _jsx(ExperimentalFeatureSettings, {}) })] }) }), _jsx("section", { className: cx(classes.tabPanel, { [classes.tabPanelActive]: activeTab === "about" }), children: _jsxs(Stack, { gap: 2, alignItems: "flex-start", children: [_jsx("header", { children: _jsx(FoxgloveLogoText, { color: "primary", className: classes.logo }) }), _jsxs(Stack, { direction: "row", alignItems: "center", gap: 1, children: [_jsxs(Typography, { variant: "body2", children: ["Foxglove Studio version ", FOXGLOVE_STUDIO_VERSION] }), _jsx(CopyButton, { size: "small", getText: () => FOXGLOVE_STUDIO_VERSION?.toString() ?? "" })] }), [
                                            aboutItems.get("resources"),
                                            aboutItems.get("products"),
                                            aboutItems.get("contact"),
                                            aboutItems.get("legal"),
                                        ].map((item) => {
                                            return (_jsxs(Stack, { gap: 1, children: [item?.subheader && _jsx(Typography, { children: item.subheader }), item?.links.map((link) => (_jsx(Link, { variant: "body2", underline: "hover", "data-testid": link.title, href: link.url, target: "_blank", children: link.title }, link.title)))] }, item?.subheader));
                                        })] }) })] })] }), _jsx(DialogActions, { className: classes.dialogActions, children: _jsx(Button, { onClick: handleClose, children: "Done" }) })] }));
}
