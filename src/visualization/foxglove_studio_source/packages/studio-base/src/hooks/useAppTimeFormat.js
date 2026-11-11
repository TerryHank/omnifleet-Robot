// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import moment from "moment-timezone";
import { useCallback, useMemo } from "react";
import { AppSetting } from "@foxglove/studio-base/AppSetting";
import { formatDate, formatTime } from "@foxglove/studio-base/util/formatTime";
import { formatTimeRaw } from "@foxglove/studio-base/util/time";
import { useAppConfigurationValue } from "./useAppConfigurationValue";
export function useAppTimeFormat() {
    const [timeFormat, setTimeFormat] = useAppConfigurationValue(AppSetting.TIME_FORMAT);
    const [timeZone] = useAppConfigurationValue(AppSetting.TIMEZONE);
    const effectiveFormat = useMemo(() => (timeFormat === "SEC" ? "SEC" : "TOD"), [timeFormat]);
    const formatDateCallback = useCallback((date) => {
        return formatDate(date, timeZone);
    }, [timeZone]);
    const formatTimeCallback = useCallback((stamp) => {
        if (effectiveFormat === "TOD") {
            return formatTime(stamp, timeZone);
        }
        else {
            return formatTimeRaw(stamp);
        }
    }, [effectiveFormat, timeZone]);
    const formatDurationCallback = useCallback((duration) => {
        if (effectiveFormat === "TOD") {
            return (moment.duration(duration.sec * 1e3).format("h:mm:ss", { trim: false }) +
                `.${duration.nsec}`);
        }
        else {
            return formatTimeRaw(duration);
        }
    }, [effectiveFormat]);
    return {
        formatDate: formatDateCallback,
        formatTime: formatTimeCallback,
        formatDuration: formatDurationCallback,
        setTimeFormat,
        timeFormat: effectiveFormat,
        timeZone,
    };
}
