import { Opaque } from "ts-essentials";
import { Immutable, MessageEvent, RegisterMessageConverterArgs, Subscription } from "@foxglove/studio";
import { Topic as PlayerTopic } from "@foxglove/studio-base/players/types";
import { ExtensionNamespace } from "@foxglove/studio-base/types/Extensions";
type ConverterKey = Opaque<string, "ConverterKey">;
type MessageConverter = RegisterMessageConverterArgs<unknown> & {
    extensionNamespace?: ExtensionNamespace;
};
type TopicSchemaConverterMap = Map<ConverterKey, MessageConverter[]>;
/**
 * Convert message into convertedMessages using the keyed converters. Modifies
 * convertedMessages in place for efficiency.
 */
export declare function convertMessage(messageEvent: Immutable<MessageEvent>, converters: Immutable<TopicSchemaConverterMap>, convertedMessages: MessageEvent[]): void;
/**
 * Returns a new map consisting of all items in `a` not present in `b`.
 */
export declare function mapDifference<K, V>(a: Map<K, V[]>, b: undefined | Map<K, V[]>): Map<K, V[]>;
export type TopicSchemaConversions = {
    unconvertedSubscriptionTopics: Set<string>;
    topicSchemaConverters: TopicSchemaConverterMap;
};
/**
 * Builds a set of topics we can render without conversion and a map of
 * converterKey -> converter arguments we use to produce converted messages.
 *
 * This will be memoized for performance so the inputs should be stable.
 */
export declare function collateTopicSchemaConversions(subscriptions: readonly Subscription[], sortedTopics: readonly PlayerTopic[], messageConverters: undefined | readonly MessageConverter[]): TopicSchemaConversions;
/**
 * Function to iterate and call function over multiple sorted arrays in sorted order across all items in all arrays.
 * Time complexity is O(t*n) where t is the number of arrays and n is the total number of items in all arrays.
 * Space complexity is O(t) where t is the number of arrays.
 * @param arrays - sorted arrays to iterate over
 * @param compareFn - function called to compare items in arrays. Returns a positive value if left is larger than right,
 *  a negative value if right is larger than left, or zero if both are equal
 * @param forEach - callback to be executed on all items in the arrays to iterate over in sorted order across all arrays
 */
export declare function forEachSortedArrays<Item>(arrays: Immutable<Item[][]>, compareFn: (a: Immutable<Item>, b: Immutable<Item>) => number, forEach: (item: Immutable<Item>) => void): void;
export {};
