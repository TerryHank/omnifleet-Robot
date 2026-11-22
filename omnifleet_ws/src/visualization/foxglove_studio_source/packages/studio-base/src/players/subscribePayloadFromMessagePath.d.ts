import { SubscriptionPreloadType, SubscribePayload } from "./types";
/**
 * Builds a SubscribePayload from a message path, requesting a specific field of the message if the
 * message path resolves to a field name.
 */
export declare function subscribePayloadFromMessagePath(path: string, preloadType?: SubscriptionPreloadType): undefined | SubscribePayload;
