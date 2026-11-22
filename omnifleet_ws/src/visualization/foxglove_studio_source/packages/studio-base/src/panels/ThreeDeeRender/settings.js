// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
export const PRECISION_DISTANCE = 3; // [1mm]
export const PRECISION_DEGREES = 1;
export function fieldSize(label, value, placeholder) {
    return {
        label,
        input: "number",
        min: 0,
        step: 0.5,
        precision: PRECISION_DISTANCE,
        value,
        placeholder: String(placeholder),
    };
}
export function fieldScaleVec3(label, value) {
    return {
        label,
        input: "vec3",
        labels: ["X", "Y", "Z"],
        step: 0.5,
        precision: PRECISION_DISTANCE,
        value,
    };
}
export function fieldLineWidth(label, value, placeholder) {
    return {
        label,
        input: "number",
        min: 0,
        step: 0.005,
        precision: 4,
        value,
        placeholder: String(placeholder),
    };
}
export function fieldGradient(label, value) {
    return { label, input: "gradient", value };
}
