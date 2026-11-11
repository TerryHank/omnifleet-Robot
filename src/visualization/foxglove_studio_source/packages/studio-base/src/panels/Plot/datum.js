// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { isTime, toSec } from "@foxglove/rostime";
export function isChartValue(value) {
    switch (typeof value) {
        case "bigint":
        case "boolean":
        case "number":
        case "string":
            return true;
        case "object":
            if (isTime(value)) {
                return true;
            }
            return false;
        default:
            return false;
    }
    return false;
}
export function getChartValue(value) {
    switch (typeof value) {
        case "bigint":
            return Number(value);
        case "boolean":
            return Number(value);
        case "number":
            return value;
        case "object":
            if (isTime(value)) {
                return toSec(value);
            }
            return undefined;
        case "string":
            return +value;
        default:
            return undefined;
    }
}
