import { MessageDefinition } from "@foxglove/message-definition";
import { Immutable } from "@foxglove/studio";
import { Topic } from "@foxglove/studio-base/src/players/types";
/**
 * Represents a message path inside a specific schema
 */
type MessagePathSuffix = Immutable<{
    /**
     * The message path suffix which can be appended to a topic name, e.g. `.header.stamp`
     */
    pathSuffix: string;
    /**
     * Human-readable type of the value or sub-message at this path, e.g. `foxglove.Point2` or `string[]`.
     */
    type: string;
    /** True if this path represents a value with no children underneath it. */
    isLeaf: boolean;
}>;
export type MessagePathSearchItem = {
    topic: Topic;
    suffix: MessagePathSuffix;
    /** Full message path, e.g. `/my_topic.header.stamp` */
    fullPath: string;
    /**
     * Offset of `suffix.pathSuffix` in the `fullPath` (differs from `topic.name.length` if the topic name requires quoting)
     */
    offset: number;
};
/**
 * Get the list of all message path search items in the TopicList (entries to be passed to fzf).
 * This includes an entry for each message path nested underneath each topic.
 */
export declare function getMessagePathSearchItems(allTopics: readonly Topic[], schemasByName: Immutable<Map<string, MessageDefinition>>): {
    items: MessagePathSearchItem[];
    itemsByTopicName: Map<string, MessagePathSearchItem[]>;
};
export {};
