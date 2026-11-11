import { MutableRefObject } from "react";
import { StoreApi } from "zustand";
import { Immutable, MessageEvent } from "@foxglove/studio";
import { AdvertiseOptions, Player, PlayerState, SubscribePayload } from "@foxglove/studio-base/players/types";
import { FramePromise } from "./pauseFrameForPromise";
import { MessagePipelineContext } from "./types";
export declare function defaultPlayerState(): PlayerState;
export type MessagePipelineInternalState = {
    dispatch: (action: MessagePipelineStateAction) => void;
    /** Reset public and private state back to initial empty values */
    reset: () => void;
    player?: Player;
    /** used to keep track of whether we need to update public.startPlayback/playUntil/etc. */
    lastCapabilities: string[];
    /** Preserves reference equality of subscriptions to minimize player subscription churn. */
    subscriptionMemoizer: (sub: SubscribePayload) => SubscribePayload;
    subscriptionsById: Map<string, Immutable<SubscribePayload[]>>;
    publishersById: {
        [key: string]: AdvertiseOptions[];
    };
    allPublishers: AdvertiseOptions[];
    /**
     * A map of topic name to the IDs that are subscribed to that topic. Incoming messages
     * are bucketed by ID so only the messages a panel subscribed to are sent to it.
     *
     * Note: Even though we avoid storing the same ID twice in the array, we use an array rather than
     * a Set because iterating over array elements is faster than iterating a Set and the "hot" path
     * for dispatching messages needs to iterate over the array of IDs.
     */
    subscriberIdsByTopic: Map<string, string[]>;
    /** This holds the last message emitted by the player on each topic. Attempt to use this before falling back to player backfill.
     */
    lastMessageEventByTopic: Map<string, MessageEvent>;
    /** Function to call when react render has completed with the latest state */
    renderDone?: () => void;
    /** Part of the state that is exposed to consumers via useMessagePipeline */
    public: MessagePipelineContext;
};
type UpdateSubscriberAction = {
    type: "update-subscriber";
    id: string;
    payloads: Immutable<SubscribePayload[]>;
};
type UpdatePlayerStateAction = {
    type: "update-player-state";
    playerState: PlayerState;
    renderDone?: () => void;
};
export type MessagePipelineStateAction = UpdateSubscriberAction | UpdatePlayerStateAction | {
    type: "set-publishers";
    id: string;
    payloads: AdvertiseOptions[];
};
export declare function createMessagePipelineStore({ promisesToWaitForRef, initialPlayer, }: {
    promisesToWaitForRef: MutableRefObject<FramePromise[]>;
    initialPlayer: Player | undefined;
}): StoreApi<MessagePipelineInternalState>;
export declare function reducer(prevState: MessagePipelineInternalState, action: MessagePipelineStateAction): MessagePipelineInternalState;
export {};
