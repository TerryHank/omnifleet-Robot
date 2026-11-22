// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
/**
 * Return the union of two 1D bounds
 */
export function unionBounds1D(a, b) {
    return { min: Math.min(a.min, b.min), max: Math.max(a.max, b.max) };
}
/**
 * Update the bounds to include the value. The bounds are updated in-place. Returns the same bounds
 * object.
 */
export function extendBounds1D(bounds, value) {
    bounds.min = Math.min(bounds.min, value);
    bounds.max = Math.max(bounds.max, value);
}
