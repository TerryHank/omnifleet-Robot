// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
//
// This file incorporates work covered by the following copyright and
// permission notice:
//
//   Copyright 2018-2021 Cruise LLC
//
//   This source code is licensed under the Apache License, Version 2.0,
//   found at http://www.apache.org/licenses/LICENSE-2.0
//   You may not use this file except in compliance with the License.
import * as R from "ramda";
import { useEffect, useMemo, useCallback } from "react";
import { iterateObjects, iterateTyped } from "@foxglove/studio-base/components/Chart/datasets";
export function getBounds(data) {
    let xMin;
    let xMax;
    let yMin;
    let yMax;
    for (const dataset of data) {
        for (const item of iterateObjects(dataset.data)) {
            if (!isNaN(item.x)) {
                xMin = Math.min(xMin ?? item.x, item.x);
                xMax = Math.max(xMax ?? item.x, item.x);
            }
            if (!isNaN(item.y)) {
                yMin = Math.min(yMin ?? item.y, item.y);
                yMax = Math.max(yMax ?? item.y, item.y);
            }
        }
    }
    if (xMin == undefined || xMax == undefined || yMin == undefined || yMax == undefined) {
        return undefined;
    }
    return { x: { min: xMin, max: xMax }, y: { min: yMin, max: yMax } };
}
export function getTypedBounds(data) {
    let xMin;
    let xMax;
    let yMin;
    let yMax;
    for (const dataset of data) {
        for (const item of iterateTyped(dataset.data)) {
            const { x, y } = item;
            if (!isNaN(x)) {
                xMin = Math.min(xMin ?? x, x);
                xMax = Math.max(xMax ?? x, x);
            }
            if (!isNaN(y)) {
                yMin = Math.min(yMin ?? y, y);
                yMax = Math.max(yMax ?? y, y);
            }
        }
    }
    if (xMin == undefined || xMax == undefined || yMin == undefined || yMax == undefined) {
        return undefined;
    }
    return { x: { min: xMin, max: xMax }, y: { min: yMin, max: yMax } };
}
function mergeBounds(a, b) {
    return {
        x: {
            min: Math.min(a.x.min, b.x.min),
            max: Math.max(a.x.max, b.x.max),
        },
        y: {
            min: Math.min(a.y.min, b.y.min),
            max: Math.max(a.y.max, b.y.max),
        },
    };
}
// Given a merging strategy, `makeMerge` returns a function that can be used to
// merge `ProviderState`s.
const makeMerge = (mergeData) => (a, b) => {
    return {
        bounds: mergeBounds(a.bounds, b.bounds),
        data: {
            datasets: R.zip(a.data.datasets, b.data.datasets).map(([aSet, bSet]) => ({
                ...aSet,
                data: mergeData(aSet.data, bSet.data),
            })),
        },
    };
};
export const mergeNormal = makeMerge((a, b) => [...a, ...b]);
export const mergeTyped = makeMerge((a, b) => a.concat(b));
export default function useProvider(view, 
// Calculates the bounds of the given datasets.
getDatasetBounds, mergeState, data, provider) {
    const [state, setState] = React.useState();
    const setFull = React.useCallback((newFull) => {
        setState({
            full: newFull,
            partial: undefined,
        });
    }, []);
    const addPartial = useCallback((newPartial) => {
        setState((oldState) => {
            if (oldState == undefined) {
                return {
                    full: undefined,
                    partial: newPartial,
                };
            }
            const { partial: oldPartial } = oldState;
            return {
                ...oldState,
                partial: oldPartial != undefined ? mergeState(oldPartial, newPartial) : newPartial,
            };
        });
    }, [mergeState]);
    useEffect(() => {
        if (provider == undefined) {
            return;
        }
        provider.register(setFull, addPartial);
    }, [provider, addPartial, setFull]);
    useEffect(() => {
        if (provider == undefined) {
            return;
        }
        provider.setView(view);
    }, [provider, view]);
    return useMemo(() => {
        if (provider != undefined) {
            if (state == undefined) {
                return undefined;
            }
            const { full, partial } = state;
            if (partial == undefined) {
                return full;
            }
            if (full == undefined) {
                return undefined;
            }
            return mergeState(full, partial);
        }
        if (data == undefined) {
            return undefined;
        }
        const bounds = getDatasetBounds(data.datasets);
        return {
            bounds: bounds ?? {
                x: { min: 0, max: 0 },
                y: { min: 0, max: 0 },
            },
            data,
        };
    }, [data, provider, state, getDatasetBounds, mergeState]);
}
