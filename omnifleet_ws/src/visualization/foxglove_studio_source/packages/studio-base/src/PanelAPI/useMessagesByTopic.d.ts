import { MessageEvent, SubscribePayload } from "@foxglove/studio-base/players/types";
/**
 * useMessagesByTopic makes it easy to request some messages on some topics.
 *
 * Using this hook will cause the panel to re-render when new messages arrive on the requested topics.
 * - During file playback the panel will re-render when the file is playing or when the user is scrubbing.
 * - During live playback the panel will re-render when new messages arrive.
 */
export declare function useMessagesByTopic(params: {
    topics: readonly string[] | SubscribePayload[];
    historySize: number;
}): Record<string, readonly MessageEvent[]>;
