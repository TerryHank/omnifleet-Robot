export type OnSelectPayload = {
    index: number;
    modKey: boolean;
    shiftKey: boolean;
};
export declare function useMultiSelection<T>(source: readonly T[]): {
    selectedIndexes: Set<number>;
    onSelect: (props: OnSelectPayload) => void;
    getSelectedIndexes: () => Set<number>;
};
