import { jsxs as _jsxs, jsx as _jsx } from "react/jsx-runtime";
import tinycolor from "tinycolor2";
import { filterMap } from "@foxglove/den/collection";
import { isTypicalFilterName } from "@foxglove/studio-base/components/MessagePathSyntax/isTypicalFilterName";
import { format, formatDuration } from "@foxglove/studio-base/util/formatTime";
import { quatToEuler } from "@foxglove/studio-base/util/quatToEuler";
const DURATION_20_YEARS_SEC = 20 * 365 * 24 * 60 * 60;
const PRIMITIVE_TYPES = ["string", "number", "bigint", "boolean"];
export function getItemString(_nodeType, data, itemType, itemString, _keyPath, timezone) {
    if (typeof data !== "object" || data == undefined) {
        return (_jsxs("span", { children: [itemType, " ", itemString] }));
    }
    const keys = Object.keys(data);
    if (keys.length === 2) {
        const { sec, nsec } = data;
        if (typeof sec === "number" && typeof nsec === "number") {
            // Values "too small" to be absolute epoch-based times are probably relative durations.
            return sec < DURATION_20_YEARS_SEC ? (formatDuration({ sec, nsec })) : (_jsx("span", { children: format({ sec, nsec }, timezone) }));
        }
    }
    // for vectors/points display length
    if (keys.length === 2) {
        const { x, y } = data;
        if (typeof x === "number" && typeof y === "number") {
            const length = Math.sqrt(x * x + y * y);
            return (_jsxs("span", { children: ["norm = ", length.toFixed(2), " ", getArrow(x, y)] }));
        }
        const { key, value } = data;
        if (key != undefined &&
            value != undefined &&
            PRIMITIVE_TYPES.includes(typeof key) &&
            PRIMITIVE_TYPES.includes(typeof value)) {
            // eslint-disable-next-line @typescript-eslint/no-base-to-string
            return `${key}: ${value}`;
        }
    }
    else if (keys.length === 3) {
        const { x, y, z } = data;
        if (typeof x === "number" && typeof y === "number" && typeof z === "number") {
            const length = Math.sqrt(x * x + y * y + z * z);
            return (_jsxs("span", { children: ["norm = ", length.toFixed(2), " ", z === 0 ? getArrow(x, y) : undefined] }));
        }
    }
    else if (keys.length === 4) {
        const { x, y, z, w } = data;
        if (typeof x === "number" &&
            typeof y === "number" &&
            typeof z === "number" &&
            typeof w === "number") {
            const [roll, pitch, yaw] = quatToEuler(x, y, z, w);
            return (_jsxs("span", { children: ["rpy = [", round(roll), ", ", round(pitch), ", ", round(yaw), "]"] }));
        }
        const { r, g, b, a } = data;
        if (typeof r === "number" &&
            typeof g === "number" &&
            typeof b === "number" &&
            typeof a === "number") {
            // print the color as hex
            return _jsx("span", { children: tinycolor({ r: r * 255, g: g * 255, b: b * 255, a }).toHex8String() });
        }
    }
    // Surface typically-used keys directly in the object summary so the user doesn't have to expand it.
    const filterKeys = filterMap(keys, (key) => {
        const value = data[key];
        if (isTypicalFilterName(key) &&
            (value == undefined || PRIMITIVE_TYPES.includes(typeof value))) {
            return `${key}: ${value}`;
        }
        return undefined;
    }).join(", ");
    return (_jsxs("span", { children: [itemType, " ", filterKeys.length > 0 ? filterKeys : itemString] }));
}
function getArrow(x, y) {
    if (x === 0 && y === 0) {
        return;
    }
    return (_jsx("span", { style: { transform: `rotate(${Math.atan2(-y, x)}rad)`, display: "inline-block" }, children: "\u2192" }));
}
function round(x, precision = 2) {
    return Number(x.toFixed(precision));
}
