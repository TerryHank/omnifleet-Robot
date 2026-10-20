import { MessagePathStructureItemMessage, MessagePath } from "@foxglove/message-path";
import { GlobalVariables } from "@foxglove/studio-base/hooks/useGlobalVariables";
import { MessageEvent, Topic } from "@foxglove/studio-base/players/types";
import { enumValuesByDatatypeAndField } from "@foxglove/studio-base/util/enums";
export type MessagePathDataItem = {
    value: unknown;
    path: string;
    constantName?: string;
};
export declare function useCachedGetMessagePathDataItems(paths: readonly string[]): (path: string, message: MessageEvent) => MessagePathDataItem[] | undefined;
export declare function fillInGlobalVariablesInPath(rosPath: MessagePath, globalVariables: GlobalVariables): MessagePath;
export declare function getMessagePathDataItems(message: MessageEvent, filledInPath: MessagePath, topicsByName: Record<string, Topic>, structures: Record<string, MessagePathStructureItemMessage>, enumValues: ReturnType<typeof enumValuesByDatatypeAndField>): MessagePathDataItem[] | undefined;
export type MessageAndData = {
    messageEvent: MessageEvent;
    queriedData: MessagePathDataItem[];
};
export type MessageDataItemsByPath = {
    readonly [key: string]: readonly MessageAndData[];
};
export declare function useDecodeMessagePathsForMessagesByTopic(paths: readonly string[]): (messagesByTopic: {
    [topicName: string]: readonly MessageEvent[];
}) => MessageDataItemsByPath;
