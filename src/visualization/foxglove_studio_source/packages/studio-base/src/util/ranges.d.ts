export type Range = {
    /** inclusive */
    start: number;
    /** exclusive */
    end: number;
};
export declare function isRangeCoveredByRanges(queryRange: Range, nonOverlappingMergedAndSortedRanges: Range[]): boolean;
export declare function missingRanges(bounds: Range, ranges: readonly Range[]): Range[];
