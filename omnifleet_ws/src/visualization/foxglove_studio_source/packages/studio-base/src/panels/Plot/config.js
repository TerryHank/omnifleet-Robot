// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { PANEL_TITLE_CONFIG_KEY } from "@foxglove/studio-base/util/layout";
/**
 * A "reference line" plot path is a numeric value. It creates a horizontal line on the plot at the
 * specified value.
 * @returns true if the series config is a reference line
 */
export function isReferenceLinePlotPathType(path) {
    return !isNaN(Number.parseFloat(path.value));
}
/**
 * Coalesces null, undefined and empty string to undefined.
 */
function presence(value) {
    if (value === "") {
        return undefined;
    }
    return value ?? undefined;
}
export function plotPathDisplayName(path, index) {
    return presence(path.label) ?? presence(path.value) ?? `Series ${index + 1}`;
}
