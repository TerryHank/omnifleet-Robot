import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { Stack } from "@mui/material";
import { useState } from "react";
import { AppSetting } from "@foxglove/studio-base/AppSetting";
import Timestamp from "@foxglove/studio-base/components/Timestamp";
import AppConfigurationContext from "@foxglove/studio-base/context/AppConfigurationContext";
import { makeMockAppConfiguration } from "@foxglove/studio-base/util/makeMockAppConfiguration";
const ABSOLUTE_TIME = { sec: 1643800942, nsec: 222222222 };
const RELATIVE_TIME = { sec: 630720000, nsec: 597648236 };
export default {
    component: Timestamp,
    title: "components/Timestamp",
};
function TimestampStory(props) {
    const { config, time } = props;
    const [value] = useState(() => makeMockAppConfiguration(config));
    return (_jsx(AppConfigurationContext.Provider, { value: value, children: _jsxs(Stack, { padding: 2, spacing: 2, children: [_jsx(Timestamp, { horizontal: true, time: time }), _jsx(Timestamp, { time: time }), _jsx(Timestamp, { disableDate: true, time: time })] }) }));
}
export const Default = {
    render: () => {
        return _jsx(TimestampStory, { config: [[AppSetting.TIMEZONE, "UTC"]], time: ABSOLUTE_TIME });
    },
};
export const TimeFormatSeconds = {
    render: () => {
        return (_jsx(TimestampStory, { config: [
                [AppSetting.TIME_FORMAT, "SEC"],
                [AppSetting.TIMEZONE, "UTC"],
            ], time: ABSOLUTE_TIME }));
    },
};
export const TimeFormatTOD = {
    render: () => {
        return (_jsx(TimestampStory, { config: [
                [AppSetting.TIME_FORMAT, "TOD"],
                [AppSetting.TIMEZONE, "UTC"],
            ], time: ABSOLUTE_TIME }));
    },
};
export const TimeFormatRelative = {
    render: () => {
        return (_jsx(TimestampStory, { config: [
                [AppSetting.TIME_FORMAT, "TOD"],
                [AppSetting.TIMEZONE, "UTC"],
            ], time: RELATIVE_TIME }));
    },
};
