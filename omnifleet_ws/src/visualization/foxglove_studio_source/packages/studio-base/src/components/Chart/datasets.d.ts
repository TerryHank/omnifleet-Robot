import { TypedData, ObjectData } from "./types";
export type Point = {
    index: number;
    x: number;
    y: number;
    label?: string | undefined;
};
/**
 * iterateObjects iterates over ObjectData, yielding a `Point` for each entry.
 */
export declare function iterateObjects(dataset: ObjectData): Generator<Point>;
/**
 * ExtractPoint maps an object type with array properties to one with the
 * arrays replaced by their element type. For example:
 * type Foo = {
 *   foo: Float32Array;
 *   bar: number[];
 *   baz: string[];
 * }
 * would be mapped to:
 * ExtractPoint<Foo> == {
 *   foo: number;
 *   bar: number;
 *   baz: string;
 * }
 * It is used to go from `TypedData`'s various incarnations to what a single
 * point would look like as a `Datum`.
 *
 * These `any`s do not introduce anything unsafe; they are necessary for
 * specifying the type (which is ultimately type-checked at point of use.)
 */
export type ExtractPoint<T extends {
    [key: string]: Array<any> | Float32Array;
}> = {
    [P in keyof T]-?: NonNullable<T[P]>[0];
} & {
    index: number;
    label: string | undefined;
};
/**
 *   Iterate over a typed dataset one point at a time. This abstraction is
 *   necessary because the Plot panel extends TypedData with more fields; we
 *   still want those to be available while iterating.
 */
export declare function iterateTyped<T extends {
    [key: string]: Array<any> | Float32Array;
}>(dataset: T[]): Generator<ExtractPoint<T>>;
export type Indices = [slice: number, offset: number];
/**
 * Given a dataset and an index inside of that dataset, return the index of the
 * slice and offset inside of that slice.
 */
export declare function findIndices(dataset: TypedData[], index: number): Indices | undefined;
