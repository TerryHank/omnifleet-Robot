import { FzfResultItem } from "fzf";
import { MessageDefinition } from "@foxglove/message-definition";
import { Immutable } from "@foxglove/studio";
import { Topic } from "@foxglove/studio-base/players/types";
import { MessagePathSearchItem } from "./getMessagePathSearchItems";
export type TopicListItem = {
    type: "topic";
    item: FzfResultItem<Topic>;
} | {
    type: "schema";
    item: FzfResultItem<MessagePathSearchItem>;
};
export type UseTopicListSearchParams = {
    topics: Immutable<Topic[]>;
    datatypes: Immutable<Map<string, MessageDefinition>>;
    filterText: string;
};
/**
 * Returns a filtered list of {@link TopicListItem}s based on the given filter text.
 */
export declare function useTopicListSearch(params: UseTopicListSearchParams): TopicListItem[];
