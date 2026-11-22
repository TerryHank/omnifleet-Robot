// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
export function compareTime(a, b) {
    return a < b ? -1 : a > b ? 1 : 0;
}
export function percentOf(start, end, target) {
    const totalDuration = end - start;
    const targetDuration = target - start;
    return Number(targetDuration) / Number(totalDuration);
}
export function interpolate(start, end, fraction) {
    const duration = Number(end - start);
    return start + BigInt(Math.round(duration * fraction));
}
