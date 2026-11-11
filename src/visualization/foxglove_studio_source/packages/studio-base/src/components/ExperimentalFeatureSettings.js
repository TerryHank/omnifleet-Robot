import { Fragment as _Fragment, jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
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
import { Checkbox, FormControlLabel, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";
import { makeStyles } from "tss-react/mui";
import { AppSetting } from "@foxglove/studio-base/AppSetting";
import Stack from "@foxglove/studio-base/components/Stack";
import { useAnalytics } from "@foxglove/studio-base/context/AnalyticsContext";
import { useAppConfigurationValue } from "@foxglove/studio-base/hooks/useAppConfigurationValue";
import { AppEvent } from "@foxglove/studio-base/services/IAnalytics";
const useStyles = makeStyles()({
    checkbox: {
        paddingTop: 0,
    },
    formControlLabel: {
        alignItems: "start",
    },
});
function useFeatures() {
    const { t } = useTranslation("appSettings");
    const features = [
        {
            key: AppSetting.ENABLE_UNIFIED_NAVIGATION,
            name: t("newAppMenu"),
            description: _jsx(_Fragment, { children: t("newAppMenuDescription") }),
        },
    ];
    if (process.env.NODE_ENV === "development") {
        features.push({
            key: AppSetting.ENABLE_LAYOUT_DEBUGGING,
            name: t("layoutDebugging"),
            description: _jsx(_Fragment, { children: t("layoutDebuggingDescription") }),
        });
    }
    return features;
}
function ExperimentalFeatureItem(props) {
    const { feature } = props;
    const { classes } = useStyles();
    const analytics = useAnalytics();
    const [enabled, setEnabled] = useAppConfigurationValue(feature.key);
    return (_jsx(FormControlLabel, { className: classes.formControlLabel, control: _jsx(Checkbox, { className: classes.checkbox, checked: enabled ?? false, onChange: (_, checked) => {
                void setEnabled(checked);
                void analytics.logEvent(AppEvent.EXPERIMENTAL_FEATURE_TOGGLE, {
                    feature: feature.key,
                    checked,
                });
            } }), label: _jsxs(Stack, { gap: 0.25, paddingLeft: 0.5, children: [_jsx(Typography, { fontWeight: 600, children: feature.name }), _jsx(Typography, { variant: "body2", color: "text.secondary", children: feature.description })] }) }));
}
export const ExperimentalFeatureSettings = () => {
    const features = useFeatures();
    const { t } = useTranslation("appSettings");
    return (_jsxs(Stack, { gap: 2, children: [features.length === 0 && (_jsx(Typography, { fontStyle: "italic", children: t("noExperimentalFeatures") })), features.map((feature) => (_jsx(ExperimentalFeatureItem, { feature: feature }, feature.key)))] }));
};
