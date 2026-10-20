// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
export const DEFAULT_PATH = Object.freeze({
    value: "",
    timestampMethod: "receiveTime",
});
function presence(value) {
    if (value === "") {
        return undefined;
    }
    return value ?? undefined;
}
export function stateTransitionPathDisplayName(path, index) {
    return presence(path.label) ?? presence(path.value) ?? `Series ${index + 1}`;
}
