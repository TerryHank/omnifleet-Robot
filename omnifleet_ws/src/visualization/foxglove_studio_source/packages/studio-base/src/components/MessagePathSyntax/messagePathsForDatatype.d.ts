import { MessagePathPart, MessagePathStructureItem, MessagePathStructureItemMessage } from "@foxglove/message-path";
import { Immutable } from "@foxglove/studio";
import { RosDatatypes } from "@foxglove/studio-base/types/RosDatatypes";
export declare function messagePathStructures(datatypes: Immutable<RosDatatypes>): Record<string, MessagePathStructureItemMessage>;
export declare function validTerminatingStructureItem(structureItem?: MessagePathStructureItem, validTypes?: readonly string[]): boolean;
/**
 * Given a datatype, the array of datatypes, and a list of valid types, list out all valid strings
 * for a MessagePathStructure and its corresponding structure item.
 */
export declare function messagePathsForStructure(structure: MessagePathStructureItemMessage, { validTypes, noMultiSlices, messagePath, }?: {
    validTypes?: readonly string[];
    noMultiSlices?: boolean;
    messagePath?: MessagePathPart[];
}): {
    path: string;
    terminatingStructureItem: MessagePathStructureItem;
}[];
export type StructureTraversalResult = {
    valid: boolean;
    msgPathPart?: MessagePathPart;
    structureItem?: MessagePathStructureItem;
};
export declare const traverseStructure: (initialStructureItem: MessagePathStructureItem | undefined, messagePath: MessagePathPart[]) => StructureTraversalResult;
