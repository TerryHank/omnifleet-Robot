// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { fromNanoSec } from "@foxglove/rostime";
import { LogLevel, } from "./types";
// Get the log message string from the log message
export function getNormalizedMessage(logMessage) {
    if ("msg" in logMessage) {
        return logMessage.msg ?? "";
    }
    else if ("message" in logMessage) {
        return logMessage.message ?? "";
    }
    return "";
}
export function getNormalizedLevel(datatype, raw) {
    switch (datatype) {
        case "foxglove_msgs/Log":
        case "foxglove_msgs/msg/Log":
        case "foxglove::Log":
        case "foxglove.Log":
            return raw.level ?? LogLevel.UNKNOWN;
        case "rosgraph_msgs/Log":
        case "rcl_interfaces/msg/Log":
            return rosLevelToLogLevel(raw.level);
    }
    return LogLevel.UNKNOWN;
}
function getNormalizedStamp(datatype, raw) {
    switch (datatype) {
        case "foxglove_msgs/Log":
        case "foxglove_msgs/msg/Log":
        case "foxglove::Log":
        case "foxglove.Log": {
            const timestamp = raw.timestamp;
            if (typeof timestamp === "bigint") {
                return fromNanoSec(timestamp);
            }
            return timestamp ?? { sec: 0, nsec: 0 };
        }
        case "rosgraph_msgs/Log":
            return raw.header.stamp;
        case "rcl_interfaces/msg/Log":
            return raw.stamp;
    }
    return {
        sec: 0,
        nsec: 0,
    };
}
export function normalizedLogMessage(datatype, raw) {
    const message = getNormalizedMessage(raw);
    const stamp = getNormalizedStamp(datatype, raw);
    const level = getNormalizedLevel(datatype, raw);
    return {
        message,
        stamp,
        level,
        name: raw.name,
        file: raw.file,
        line: raw.line,
    };
}
function rosLevelToLogLevel(rosLevel) {
    switch (rosLevel) {
        case 1:
        case 10:
            return LogLevel.DEBUG;
        case 2:
        case 20:
            return LogLevel.INFO;
        case 4:
        case 30:
            return LogLevel.WARN;
        case 8:
        case 40:
            return LogLevel.ERROR;
        case 16:
        case 50:
            return LogLevel.FATAL;
        default:
            return LogLevel.UNKNOWN;
    }
}
