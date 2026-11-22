import { createElement as _createElement } from "react";
import { jsxs as _jsxs, jsx as _jsx, Fragment as _Fragment } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import Brightness5Icon from "@mui/icons-material/Brightness5";
import ComputerIcon from "@mui/icons-material/Computer";
import DarkModeIcon from "@mui/icons-material/DarkMode";
import QuestionAnswerOutlinedIcon from "@mui/icons-material/QuestionAnswerOutlined";
import WebIcon from "@mui/icons-material/Web";
import { Autocomplete, Checkbox, Divider, FormControl, FormControlLabel, FormLabel, MenuItem, Select, TextField, ToggleButton, ToggleButtonGroup, } from "@mui/material";
import moment from "moment-timezone";
import { useCallback, useMemo } from "react";
import { useTranslation } from "react-i18next";
import { makeStyles } from "tss-react/mui";
import { filterMap } from "@foxglove/den/collection";
import { AppSetting } from "@foxglove/studio-base/AppSetting";
import OsContextSingleton from "@foxglove/studio-base/OsContextSingleton";
import Stack from "@foxglove/studio-base/components/Stack";
import { useAppTimeFormat } from "@foxglove/studio-base/hooks";
import { useAppConfigurationValue } from "@foxglove/studio-base/hooks/useAppConfigurationValue";
import { reportError } from "@foxglove/studio-base/reportError";
import { LaunchPreferenceValue } from "@foxglove/studio-base/types/LaunchPreferenceValue";
import { formatTime } from "@foxglove/studio-base/util/formatTime";
import { formatTimeRaw } from "@foxglove/studio-base/util/time";
const MESSAGE_RATES = [1, 3, 5, 10, 15, 20, 30, 60];
const LANGUAGE_OPTIONS = [
    { key: "en", value: "English" },
    { key: "zh", value: "中文" },
    { key: "ja", value: "日本語" },
];
const useStyles = makeStyles()((theme) => ({
    autocompleteInput: {
        "&.MuiOutlinedInput-input": {
            padding: 0,
        },
    },
    checkbox: {
        "&.MuiCheckbox-root": {
            paddingTop: 0,
        },
    },
    formControlLabel: {
        "&.MuiFormControlLabel-root": {
            alignItems: "start",
        },
    },
    toggleButton: {
        display: "flex !important",
        flexDirection: "column",
        gap: theme.spacing(0.75),
        lineHeight: "1 !important",
    },
}));
function formatTimezone(name) {
    const tz = moment.tz(name);
    const zoneAbbr = tz.zoneAbbr();
    const offset = tz.utcOffset();
    const offsetStr = (offset >= 0 ? "+" : "") + moment.duration(offset, "minutes").format("hh:mm", { trim: false });
    if (name === zoneAbbr) {
        return `${zoneAbbr} (${offsetStr})`;
    }
    return `${name} (${zoneAbbr}, ${offsetStr})`;
}
export function ColorSchemeSettings() {
    const { classes } = useStyles();
    const [colorScheme = "system", setColorScheme] = useAppConfigurationValue(AppSetting.COLOR_SCHEME);
    const { t } = useTranslation("appSettings");
    const handleChange = useCallback((_event, value) => {
        if (value != undefined) {
            void setColorScheme(value);
        }
    }, [setColorScheme]);
    return (_jsxs(Stack, { children: [_jsxs(FormLabel, { children: [t("colorScheme"), ":"] }), _jsxs(ToggleButtonGroup, { color: "primary", size: "small", fullWidth: true, exclusive: true, value: colorScheme, onChange: handleChange, children: [_jsxs(ToggleButton, { className: classes.toggleButton, value: "dark", children: [_jsx(DarkModeIcon, {}), " ", t("dark")] }), _jsxs(ToggleButton, { className: classes.toggleButton, value: "light", children: [_jsx(Brightness5Icon, {}), " ", t("light")] }), _jsxs(ToggleButton, { className: classes.toggleButton, value: "system", children: [_jsx(ComputerIcon, {}), " ", t("followSystem")] })] })] }));
}
export function TimezoneSettings() {
    const { classes } = useStyles();
    const { t } = useTranslation("appSettings");
    const [timezone, setTimezone] = useAppConfigurationValue(AppSetting.TIMEZONE);
    const detectItem = useMemo(() => ({
        key: "detect",
        label: `Detect from system: ${formatTimezone(moment.tz.guess())}`,
        data: undefined,
    }), []);
    const fixedItems = useMemo(() => [
        detectItem,
        { key: "zone:UTC", label: `${formatTimezone("UTC")}`, data: "UTC" },
        {
            key: "sep",
            label: "",
            divider: true,
        },
    ], [detectItem]);
    const timezoneItems = useMemo(() => filterMap(moment.tz.names(), (name) => {
        // UTC is always hoisted to the top in fixedItems
        if (name === "UTC") {
            return undefined;
        }
        return { key: `zone:${name}`, label: formatTimezone(name), data: name };
    }), []);
    const allItems = useMemo(() => [...fixedItems, ...timezoneItems], [fixedItems, timezoneItems]);
    const selectedItem = useMemo(() => {
        if (timezone != undefined) {
            return allItems.find((item) => item.data === timezone) ?? detectItem;
        }
        return detectItem;
    }, [allItems, detectItem, timezone]);
    return (_jsxs(FormControl, { fullWidth: true, children: [_jsxs(FormLabel, { children: [t("displayTimestampsIn"), ":"] }), _jsx(Autocomplete, { options: [...fixedItems, ...timezoneItems], value: selectedItem, renderOption: (props, option) => option.divider === true ? (_jsx(Divider, {}, option.key)) : (_createElement("li", { ...props, key: option.key }, option.label)), renderInput: (params) => (_jsx(TextField, { ...params, inputProps: { ...params.inputProps, className: classes.autocompleteInput } })), onChange: (_event, value) => void setTimezone(value?.data) })] }));
}
export function TimeFormat({ orientation = "vertical", }) {
    const { timeFormat, setTimeFormat } = useAppTimeFormat();
    const { t } = useTranslation("appSettings");
    const [timezone] = useAppConfigurationValue(AppSetting.TIMEZONE);
    const exampleTime = { sec: 946713600, nsec: 0 };
    return (_jsxs(Stack, { children: [_jsxs(FormLabel, { children: [t("timestampFormat"), ":"] }), _jsxs(ToggleButtonGroup, { color: "primary", size: "small", orientation: orientation, fullWidth: true, exclusive: true, value: timeFormat, onChange: (_, value) => value != undefined && void setTimeFormat(value), children: [_jsx(ToggleButton, { value: "SEC", "data-testid": "timeformat-seconds", children: formatTimeRaw(exampleTime) }), _jsx(ToggleButton, { value: "TOD", "data-testid": "timeformat-local", children: formatTime(exampleTime, timezone) })] })] }));
}
export function LaunchDefault() {
    const { classes } = useStyles();
    const { t } = useTranslation("appSettings");
    const [preference, setPreference] = useAppConfigurationValue(AppSetting.LAUNCH_PREFERENCE);
    let sanitizedPreference;
    switch (preference) {
        case LaunchPreferenceValue.WEB:
        case LaunchPreferenceValue.DESKTOP:
        case LaunchPreferenceValue.ASK:
            sanitizedPreference = preference;
            break;
        default:
            sanitizedPreference = LaunchPreferenceValue.WEB;
    }
    return (_jsxs(Stack, { children: [_jsxs(FormLabel, { children: [t("openLinksIn"), ":"] }), _jsxs(ToggleButtonGroup, { color: "primary", size: "small", fullWidth: true, exclusive: true, value: sanitizedPreference, onChange: (_, value) => value != undefined && void setPreference(value), children: [_jsxs(ToggleButton, { value: LaunchPreferenceValue.WEB, className: classes.toggleButton, children: [_jsx(WebIcon, {}), " ", t("webApp")] }), _jsxs(ToggleButton, { value: LaunchPreferenceValue.DESKTOP, className: classes.toggleButton, children: [_jsx(ComputerIcon, {}), " ", t("desktopApp")] }), _jsxs(ToggleButton, { value: LaunchPreferenceValue.ASK, className: classes.toggleButton, children: [_jsx(QuestionAnswerOutlinedIcon, {}), " ", t("askEachTime")] })] })] }));
}
export function MessageFramerate() {
    const { t } = useTranslation("appSettings");
    const [messageRate, setMessageRate] = useAppConfigurationValue(AppSetting.MESSAGE_RATE);
    const options = useMemo(() => MESSAGE_RATES.map((rate) => ({ key: rate, text: `${rate}`, data: rate })), []);
    return (_jsxs(Stack, { children: [_jsxs(FormLabel, { children: [t("messageRate"), " (Hz):"] }), _jsx(Select, { value: messageRate ?? 60, fullWidth: true, onChange: (event) => void setMessageRate(event.target.value), children: options.map((option) => (_jsx(MenuItem, { value: option.key, children: option.text }, option.key))) })] }));
}
export function AutoUpdate() {
    const [updatesEnabled = true, setUpdatedEnabled] = useAppConfigurationValue(AppSetting.UPDATES_ENABLED);
    const { classes } = useStyles();
    return (_jsxs(_Fragment, { children: [_jsx(FormLabel, { children: "Updates:" }), _jsx(FormControlLabel, { className: classes.formControlLabel, control: _jsx(Checkbox, { className: classes.checkbox, checked: updatesEnabled, onChange: (_event, checked) => void setUpdatedEnabled(checked) }), label: "\u81EA\u52A8\u5B89\u88C5\u66F4\u65B0" })] }));
}
export function RosPackagePath() {
    const [rosPackagePath, setRosPackagePath] = useAppConfigurationValue(AppSetting.ROS_PACKAGE_PATH);
    const rosPackagePathPlaceholder = useMemo(() => OsContextSingleton?.getEnvVar("ROS_PACKAGE_PATH"), []);
    return (_jsx(TextField, { fullWidth: true, label: "ROS_PACKAGE_PATH", placeholder: rosPackagePathPlaceholder, value: rosPackagePath ?? "", onChange: (event) => void setRosPackagePath(event.target.value) }));
}
export function LanguageSettings() {
    const { t, i18n } = useTranslation("appSettings");
    const [selectedLanguage = "zh", setSelectedLanguage] = useAppConfigurationValue(AppSetting.LANGUAGE);
    const onChangeLanguage = useCallback((event) => {
        const lang = event.target.value;
        void setSelectedLanguage(lang);
        i18n.changeLanguage(lang).catch((error) => {
            console.error("Failed to switch languages", error);
            reportError(error);
        });
    }, [i18n, setSelectedLanguage]);
    const options = useMemo(() => LANGUAGE_OPTIONS.map((language) => ({
        key: language.key,
        text: `${language.value}`,
        data: language.key,
    })), []);
    return (_jsxs(Stack, { children: [_jsxs(FormLabel, { children: [t("language"), ":"] }), _jsx(Select, { value: selectedLanguage, fullWidth: true, onChange: onChangeLanguage, children: options.map((option) => (_jsx(MenuItem, { value: option.key, children: option.text }, option.key))) })] }));
}
