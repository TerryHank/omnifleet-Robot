import { Immutable } from "@foxglove/studio";
export type Bounds1D = {
    min: number;
    max: number;
};
/**
 * Describes the limits of a rectangular area in 2d space.
 */
export type Bounds = {
    x: Bounds1D;
    y: Bounds1D;
};
/**
 * Return the union of two 1D bounds
 */
export declare function unionBounds1D(a: Immutable<Bounds1D>, b: Immutable<Bounds1D>): Bounds1D;
/**
 * Update the bounds to include the value. The bounds are updated in-place. Returns the same bounds
 * object.
 */
export declare function extendBounds1D(bounds: Bounds1D, value: number): void;
