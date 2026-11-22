import { Immutable } from "@foxglove/studio";
import { SubscribePayload } from "@foxglove/studio-base/players/types";
/**
 * Create a deep equal memoized identify function. Used for stabilizing the subscription payloads we
 * send on to the player.
 *
 * Note that this has unlimited cache size so it should be managed by some containing scope.
 */
export declare function makeSubscriptionMemoizer(): (val: SubscribePayload) => SubscribePayload;
/**
 * Merges individual topic subscriptions into a set of subscriptions to send on to the player.
 *
 * If any client requests a "whole" subscription to a topic then all fields will be fetched for that
 * topic. If various clients request different slices of a topic then we request the union of all
 * requested slices.
 */
export declare function mergeSubscriptions(subscriptions: Immutable<SubscribePayload[]>): Immutable<SubscribePayload[]>;
