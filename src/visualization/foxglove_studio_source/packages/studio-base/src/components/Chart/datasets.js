// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import * as R from "ramda";
/**
 * iterateObjects iterates over ObjectData, yielding a `Point` for each entry.
 */
export function* iterateObjects(dataset) {
    let index = 0;
    for (const datum of dataset) {
        if (datum == undefined) {
            index++;
            continue;
        }
        const { x, y, label } = datum;
        yield {
            index,
            x,
            y,
            label,
        };
        index++;
    }
}
/**
 *   Iterate over a typed dataset one point at a time. This abstraction is
 *   necessary because the Plot panel extends TypedData with more fields; we
 *   still want those to be available while iterating.
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function* iterateTyped(dataset) {
    const point = {
        index: 0,
        label: undefined,
    };
    let index = 0;
    for (const slice of dataset) {
        // Find a property for which we can check the length
        const first = R.head(Object.values(slice));
        if (first == undefined) {
            continue;
        }
        for (let j = 0; j < first.length; j++) {
            for (const key of Object.keys(slice)) {
                point[key] = slice[key]?.[j];
            }
            point.index = index;
            index++;
            yield point;
        }
    }
}
/**
 * Given a dataset and an index inside of that dataset, return the index of the
 * slice and offset inside of that slice.
 */
export function findIndices(dataset, index) {
    let offset = index;
    for (let i = 0; i < dataset.length; i++) {
        const slice = dataset[i];
        if (slice == undefined) {
            continue;
        }
        const { x: { length: numElements }, } = slice;
        if (offset === numElements && i === dataset.length - 1) {
            return [i, offset];
        }
        if (offset >= numElements) {
            offset -= numElements;
            continue;
        }
        return [i, offset];
    }
    return undefined;
}
