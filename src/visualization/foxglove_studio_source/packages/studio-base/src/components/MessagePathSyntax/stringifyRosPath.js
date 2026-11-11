// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
/**
 * Return the string representation of the ros path
 */
export function stringifyMessagePath(path) {
    return (path.topicNameRepr +
        path.messagePath.map(stringifyMessagePathPart).join("") +
        (path.modifier ? `.@${path.modifier}` : ""));
}
function stringifyMessagePathPart(part) {
    switch (part.type) {
        case "name":
            return `.${part.repr}`;
        case "filter":
            return filterToString(part);
        case "slice":
            return sliceToString(part);
    }
    return "";
}
function sliceToString(slice) {
    if (typeof slice.start === "number" && typeof slice.end === "number") {
        if (slice.start === slice.end) {
            return `[${slice.start}]`;
        }
        if (slice.start === 0) {
            return `[:${slice.end === Infinity ? "" : slice.end}]`;
        }
        return `[${slice.start === Infinity ? "" : slice.start}:${slice.end === Infinity ? "" : slice.end}]`;
    }
    const startStr = slicePartToString(slice.start);
    const endStr = slicePartToString(slice.end);
    if (startStr === endStr) {
        return `[${startStr}]`;
    }
    return `[${startStr}:${endStr}]`;
}
function slicePartToString(slicePart) {
    if (typeof slicePart === "number") {
        if (slicePart === Infinity) {
            return "";
        }
        return String(slicePart);
    }
    return `$${slicePart.variableName}`;
}
function filterToString(filter) {
    if (typeof filter.value === "object") {
        return `{${filter.repr}}`;
    }
    return `{${filter.path.join(".")}==${typeof filter.value === "bigint" ? filter.value.toString() : JSON.stringify(filter.value)}}`;
}
