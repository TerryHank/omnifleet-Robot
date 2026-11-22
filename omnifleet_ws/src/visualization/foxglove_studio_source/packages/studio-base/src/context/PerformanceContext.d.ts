/// <reference types="react" />
import { Opaque } from "ts-essentials";
export type PerformanceMetricID = Opaque<number, "PerformanceMetricID">;
export type PerformanceMetric = {
    id: PerformanceMetricID;
    /** Name, such as "Execution time" */
    name: string;
    /** Human-readable unit, such as "ms per frame" */
    unit: string;
};
/** An object that records performance timing information. */
export interface IPerformanceRegistry {
    /** Register a new metric with the given name and unit */
    registerMetric(metric: Omit<PerformanceMetric, "id">): PerformanceMetricID;
    /** Unregister a previously registered metric */
    unregisterMetric(metricId: PerformanceMetricID): void;
    /**
     * Record data for a metric.
     *
     * @param timestamp milliseconds, e.g. from performance.now()
     * @param value Arbitrary value, displayed with {@link PerformanceMetric.unit} for human-readability
     */
    addMeasurement(metricId: PerformanceMetricID, timestamp: number, value: number): void;
    /**
     * Starts measuring time and returns a Disposable that finishes & records the measurement when it
     * is disposed at the end of the enclosing scope. Use with `using timer = scopeTimer(...);`.
     *
     * https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-2.html#using-declarations-and-explicit-resource-management
     */
    scopeTimer(metricId: PerformanceMetricID): Disposable;
}
export declare const PerformanceContext: import("react").Context<IPerformanceRegistry>;
export declare function usePerformance(): IPerformanceRegistry;
