// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { NumericType } from "@foxglove/schemas";
import { PointFieldType, } from "./ros";
export function normalizeTime(time) {
    if (!time) {
        return { sec: 0, nsec: 0 };
    }
    return { sec: time.sec ?? 0, nsec: time.nsec ?? 0 };
}
export function normalizeByteArray(byteArray) {
    if (byteArray == undefined) {
        return new Uint8Array(0);
    }
    else if (byteArray instanceof Uint8Array) {
        return byteArray;
    }
    else if (Array.isArray(byteArray) || byteArray instanceof ArrayBuffer) {
        return new Uint8Array(byteArray);
    }
    else {
        return new Uint8Array(0);
    }
}
export function normalizeInt8Array(int8Array) {
    if (int8Array == undefined) {
        return new Int8Array(0);
    }
    else if (int8Array instanceof Int8Array) {
        return int8Array;
    }
    else if (Array.isArray(int8Array) || int8Array instanceof ArrayBuffer) {
        return new Int8Array(int8Array);
    }
    else {
        return new Int8Array(0);
    }
}
export function normalizeFloat32Array(array) {
    if (array == undefined) {
        return new Float32Array(0);
    }
    else if (array instanceof Float32Array) {
        return array;
    }
    else if (Array.isArray(array) ||
        array instanceof ArrayBuffer ||
        array instanceof Float64Array) {
        return new Float32Array(array);
    }
    else {
        return new Float32Array(0);
    }
}
export function normalizeVector3(vector) {
    if (!vector) {
        return { x: 0, y: 0, z: 0 };
    }
    return { x: vector.x ?? 0, y: vector.y ?? 0, z: vector.z ?? 0 };
}
export function normalizeVector3s(vectors) {
    if (!vectors) {
        return [];
    }
    return vectors.map(normalizeVector3);
}
export function normalizeMatrix6(mat) {
    if (!mat || mat.length !== 36 || typeof mat[0] !== "number") {
        // prettier-ignore
        return [
            1, 0, 0, 0, 0, 0,
            0, 1, 0, 0, 0, 0,
            0, 0, 1, 0, 0, 0,
            0, 0, 0, 1, 0, 0,
            0, 0, 0, 0, 1, 0,
            0, 0, 0, 0, 0, 1
        ];
    }
    return mat;
}
// ts-unused-exports:disable-next-line
export function normalizeQuaternion(quat) {
    if (!quat) {
        return { x: 0, y: 0, z: 0, w: 1 };
    }
    return { x: quat.x ?? 0, y: quat.y ?? 0, z: quat.z ?? 0, w: quat.w ?? 0 };
}
export function normalizeColorRGBA(color) {
    if (!color) {
        return { r: 0, g: 0, b: 0, a: 1 };
    }
    // alpha defaults to 1 if unspecified
    return { r: color.r ?? 0, g: color.g ?? 0, b: color.b ?? 0, a: color.a ?? 1 };
}
export function normalizeColorRGBAs(colors) {
    if (!colors) {
        return [];
    }
    return colors.map(normalizeColorRGBA);
}
export function normalizePose(pose) {
    return {
        position: normalizeVector3(pose?.position),
        orientation: normalizeQuaternion(pose?.orientation),
    };
}
export function normalizeHeader(header) {
    return {
        frame_id: header?.frame_id ?? "",
        stamp: normalizeTime(header?.stamp),
        seq: header?.seq,
    };
}
// ts-unused-exports:disable-next-line
export function normalizeTransform(transform) {
    return {
        translation: normalizeVector3(transform?.translation),
        rotation: normalizeQuaternion(transform?.rotation),
    };
}
export function normalizeTransformStamped(transform) {
    return {
        header: normalizeHeader(transform?.header),
        child_frame_id: transform?.child_frame_id ?? "",
        transform: normalizeTransform(transform?.transform),
    };
}
export function normalizeTFMessage(tfMessage) {
    return {
        transforms: (tfMessage?.transforms ?? []).map(normalizeTransformStamped),
    };
}
export function normalizeFrameTransform(frameTransform) {
    return {
        timestamp: normalizeTime(frameTransform?.timestamp),
        parent_frame_id: frameTransform?.parent_frame_id ?? "",
        child_frame_id: frameTransform?.child_frame_id ?? "",
        translation: normalizeVector3(frameTransform?.translation ?? frameTransform?.transform?.translation),
        rotation: normalizeQuaternion(frameTransform?.rotation ?? frameTransform?.transform?.rotation),
    };
}
export function normalizeFrameTransforms(frameTransforms) {
    return {
        transforms: (frameTransforms?.transforms ?? []).map(normalizeFrameTransform),
    };
}
export function numericTypeToPointFieldType(type) {
    switch (type) {
        case NumericType.UINT8:
            return PointFieldType.UINT8;
        case NumericType.INT8:
            return PointFieldType.INT8;
        case NumericType.UINT16:
            return PointFieldType.UINT16;
        case NumericType.INT16:
            return PointFieldType.INT16;
        case NumericType.UINT32:
            return PointFieldType.UINT32;
        case NumericType.INT32:
            return PointFieldType.INT32;
        case NumericType.FLOAT32:
            return PointFieldType.FLOAT32;
        case NumericType.FLOAT64:
            return PointFieldType.FLOAT64;
        default:
            return PointFieldType.UNKNOWN;
    }
}
