import { MessageDefinitionMap } from "@foxglove/mcap-support/src/types";
export declare const OBJECT_BASE_SIZE: number;
/**
 * Estimates the memory size of a deserialized message object based on the schema definition.
 *
 * The estimation is by no means accurate but may in certain situations (especially when there are
 * no dynamic fields such as arrays or strings) give a better estimation than the number of bytes
 * of the serialized message. For estimating memory size, we assume a V8 JS engine (probably
 * similar for other engines).
 *
 * @param datatypes Map of data types
 * @param typeName Name of the data type
 * @param knownTypeSizes Map of known type sizes (for caching purposes)
 * @returns Estimated object size in bytes
 */
export declare function estimateMessageObjectSize(datatypes: MessageDefinitionMap, typeName: string, knownTypeSizes: Map<string, number>, checkedTypes?: string[]): number;
/**
 * Determine the size of each schema sub-field. This can be used for estimating
 * the size of sliced messages.
 *
 * @param datatypes
 * @param typeName
 * @param knownTypeSizes
 * @returns
 */
export declare function estimateMessageFieldSizes(datatypes: MessageDefinitionMap, typeName: string, knownTypeSizes: Map<string, number>): Record<string, number>;
/**
 * Estimate the size in bytes of an arbitrary object or primitive.
 * @param obj Object or primitive to estimate the size for
 * @returns Estimated size in bytes
 */
export declare function estimateObjectSize(obj: unknown): number;
