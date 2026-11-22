import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { Button, Checkbox, Dialog, DialogContent, DialogTitle, FormControlLabel, Grid, Typography, } from "@mui/material";
import { useState } from "react";
import { makeStyles } from "tss-react/mui";
import { useSessionStorageValue } from "@foxglove/hooks";
import { AppSetting } from "@foxglove/studio-base/AppSetting";
import Stack from "@foxglove/studio-base/components/Stack";
import { useAppConfigurationValue } from "@foxglove/studio-base/hooks";
import { LaunchPreferenceValue } from "@foxglove/studio-base/types/LaunchPreferenceValue";
const useStyles = makeStyles()((theme) => ({
    button: {
        textAlign: "left",
        justifyContent: "flex-start",
        padding: theme.spacing(2),
        gap: theme.spacing(1.5),
        borderColor: theme.palette.divider,
        height: "100%",
    },
    paper: {
        maxWidth: 480,
    },
    dialogTitle: {
        textAlign: "center",
        fontSize: theme.typography.h2.fontSize,
        paddingBlock: theme.spacing(3),
    },
}));
export function LaunchPreferenceScreen() {
    const { classes } = useStyles();
    const [globalPreference, setGlobalPreference] = useAppConfigurationValue(AppSetting.LAUNCH_PREFERENCE);
    const [, setSessionPreference] = useSessionStorageValue(AppSetting.LAUNCH_PREFERENCE);
    const [rememberPreference, setRememberPreference] = useState(globalPreference != undefined);
    async function launchInWeb() {
        setSessionPreference(LaunchPreferenceValue.WEB); // always set session preference to allow overriding the URL param
        await setGlobalPreference(rememberPreference ? LaunchPreferenceValue.WEB : undefined);
    }
    async function launchInDesktop() {
        setSessionPreference(LaunchPreferenceValue.DESKTOP); // always set session preference to allow overriding the URL param
        await setGlobalPreference(rememberPreference ? LaunchPreferenceValue.DESKTOP : undefined);
    }
    function toggleRememberPreference() {
        setRememberPreference(!rememberPreference);
    }
    const actions = [
        {
            key: LaunchPreferenceValue.WEB,
            primary: "Web",
            secondary: "Requires Chrome v76+",
            onClick: () => void launchInWeb(),
        },
        {
            key: LaunchPreferenceValue.DESKTOP,
            primary: "Desktop App",
            secondary: "For Linux, Windows, and macOS",
            onClick: () => void launchInDesktop(),
        },
    ];
    return (_jsxs(Dialog, { open: true, classes: { paper: classes.paper }, children: [_jsx(DialogTitle, { className: classes.dialogTitle, children: "Launch Foxglove Studio" }), _jsx(DialogContent, { children: _jsxs(Grid, { container: true, spacing: 1, children: [actions.map((action) => (_jsx(Grid, { item: true, xs: 12, sm: 6, children: _jsx(Button, { className: classes.button, fullWidth: true, color: "inherit", variant: "outlined", onClick: action.onClick, children: _jsxs(Stack, { flex: "auto", zeroMinWidth: true, children: [_jsx(Typography, { variant: "subtitle1", color: "text.primary", children: action.primary }), _jsx(Typography, { variant: "body2", color: "text.secondary", children: action.secondary })] }) }) }, action.key))), _jsx(Grid, { item: true, xs: 12, children: _jsx(FormControlLabel, { label: "\u8BB0\u4F4F\u6211\u7684\u9009\u62E9", control: _jsx(Checkbox, { color: "primary", checked: rememberPreference, onChange: toggleRememberPreference }) }) })] }) })] }));
}
