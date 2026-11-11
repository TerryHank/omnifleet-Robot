// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
export var PrimitiveType;
(function (PrimitiveType) {
    PrimitiveType["CUBES"] = "CUBES";
    PrimitiveType["MODELS"] = "MODELS";
    PrimitiveType["LINES"] = "LINES";
    PrimitiveType["CYLINDERS"] = "CYLINDERS";
    PrimitiveType["ARROWS"] = "ARROWS";
    PrimitiveType["SPHERES"] = "SPHERES";
    PrimitiveType["TEXTS"] = "TEXTS";
    PrimitiveType["TRIANGLES"] = "TRIANGLES";
})(PrimitiveType || (PrimitiveType = {}));
export const ALL_PRIMITIVE_TYPES = [
    PrimitiveType.CUBES,
    PrimitiveType.MODELS,
    PrimitiveType.LINES,
    PrimitiveType.CYLINDERS,
    PrimitiveType.ARROWS,
    PrimitiveType.SPHERES,
    PrimitiveType.TEXTS,
    PrimitiveType.TRIANGLES,
];
