import { jsx as _jsx } from "react/jsx-runtime";
import { useState } from "react";
import { AppSetting } from "@foxglove/studio-base/AppSetting";
import MockMessagePipelineProvider from "@foxglove/studio-base/components/MessagePipeline/MockMessagePipelineProvider";
import AppConfigurationContext from "@foxglove/studio-base/context/AppConfigurationContext";
import { PlayerPresence } from "@foxglove/studio-base/players/types";
import { makeMockAppConfiguration } from "@foxglove/studio-base/util/makeMockAppConfiguration";
import { EndTimestamp } from "./EndTimestamp";
const ABSOLUTE_TIME = { sec: 1643800942, nsec: 222222222 };
const RELATIVE_TIME = { sec: 630720000, nsec: 597648236 };
export default {
    title: "components/AppBar/EndTimestamp",
    component: EndTimestamp,
    args: {
        timezone: "UTC",
        time: ABSOLUTE_TIME,
    },
    decorators: [
        (Story, ctx) => {
            const { args: { timeFormat, timezone, time, ...args }, } = ctx;
            const [value] = useState(() => makeMockAppConfiguration([
                [AppSetting.TIMEZONE, timezone],
                [AppSetting.TIME_FORMAT, timeFormat],
            ]));
            return (_jsx(AppConfigurationContext.Provider, { value: value, children: _jsx(MockMessagePipelineProvider, { endTime: time, presence: PlayerPresence.PRESENT, children: _jsx("div", { style: { padding: 16 }, children: _jsx(Story, { ...args }) }) }) }));
        },
    ],
};
export const Default = {};
export const TimeFormatSeconds = {
    args: { timeFormat: "SEC" },
};
export const TimeFormatTOD = {
    args: { timeFormat: "TOD" },
};
export const TimeFormatRelative = {
    args: { time: RELATIVE_TIME },
};
