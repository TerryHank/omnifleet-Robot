import { Immutable } from "@foxglove/studio";
import { MessageEvent, SubscribePayload } from "@foxglove/studio-base/players/types";
export type MessageBlock = Immutable<{
    [topicName: string]: MessageEvent[];
}>;
export declare function useBlocksSubscriptions(subscriptions: Immutable<SubscribePayload[]>): readonly MessageBlock[];
