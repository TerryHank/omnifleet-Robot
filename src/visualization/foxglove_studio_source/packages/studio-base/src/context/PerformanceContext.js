// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { createContext, useContext } from "react";
// Ensure Symbol.dispose and Symbol.asyncDispose are defined
// https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-2.html
// eslint-disable-next-line @typescript-eslint/no-explicit-any
Symbol.dispose ??= Symbol("Symbol.dispose");
// eslint-disable-next-line @typescript-eslint/no-explicit-any
Symbol.asyncDispose ??= Symbol("Symbol.asyncDispose");
export const PerformanceContext = createContext({
    registerMetric() {
        return NaN;
    },
    unregisterMetric() { },
    addMeasurement() { },
    scopeTimer() {
        return { [Symbol.dispose]() { } };
    },
});
PerformanceContext.displayName = "PerformanceContext";
// ts-unused-exports:disable-next-line
export function usePerformance() {
    return useContext(PerformanceContext);
}
