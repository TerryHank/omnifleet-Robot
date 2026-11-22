import { MessageEvent, SubscribePayload, SubscriptionPreloadType } from "@foxglove/studio-base/players/types";
type MessageReducer<T> = (state: T, message: MessageEvent) => T;
type MessagesReducer<T> = (state: T, messages: readonly MessageEvent[]) => T;
type Params<T> = {
    /**
     * Topics to subscribe to. Can be a list of topic strings or `SubscribePayload` objects.
     */
    topics: readonly string[] | SubscribePayload[];
    /**
     * Preload type to be used for topic string subscriptions.
     * Has no effect on `SubscribePayload` topic subscriptions.
     * @default "partial"
     */
    preloadType?: SubscriptionPreloadType;
    /**
     * Called on intialization, seek, and when reducers change.
     * @param state - Immutable. `undefined` when called on initialization or seek. Otherwise, the current state.
     * @returns - New state. Must be new reference to trigger rerender.
     */
    restore: (state: T | undefined) => T;
    /**
     * Called for each new message with the current state (Immutable).
     * Return new reference to trigger rerender.
     */
    addMessage?: MessageReducer<T>;
    /**
     * Called for all new messages with the current state (Immutable).
     * Return new reference to trigger rerender.
     */
    addMessages?: MessagesReducer<T>;
};
export declare function useMessageReducer<T>(props: Params<T>): T;
export {};
