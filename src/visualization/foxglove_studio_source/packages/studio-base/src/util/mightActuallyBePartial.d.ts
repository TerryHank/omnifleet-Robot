/**
 * Marks a value as possibly having missing properties even if the specified type is
 * complete. Used to manually add checks for missing values without flagging the
 * @typescript-eslint/no-unnecessary-condition rule.
 *
 * If you need this it probably means your types are not rigorous enough.
 */
export declare function mightActuallyBePartial<T>(value: T): Partial<T>;
