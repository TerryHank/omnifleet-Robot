import { MessagePathStructureItem } from "@foxglove/message-path";
export type ValueAction = {
    singleSlicePath: string;
    multiSlicePath: string;
    primitiveType: string;
    filterPath: string;
};
export declare function getValueActionForValue(rootValue: unknown, rootStructureItem: MessagePathStructureItem | undefined, keyPath: (number | string)[]): ValueAction | undefined;
export declare const getStructureItemForPath: (rootStructureItem: MessagePathStructureItem | undefined, keyPath: (number | string)[]) => MessagePathStructureItem | undefined;
