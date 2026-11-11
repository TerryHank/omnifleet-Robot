declare const sortFn: (a: string | number, b: string | number) => number;
type StringOrNumberFields<T> = T extends Record<string, unknown> ? {
    [K in keyof T]: T[K] extends string | number ? K : never;
}[keyof T] : never;
declare function naturalSort(): typeof sortFn;
declare function naturalSort<T, K extends StringOrNumberFields<T>>(key: K): (a: T, b: T) => number;
export default naturalSort;
