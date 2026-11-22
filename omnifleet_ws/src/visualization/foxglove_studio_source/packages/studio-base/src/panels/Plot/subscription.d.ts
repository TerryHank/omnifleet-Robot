import type { MessagePath } from "@foxglove/message-path";
import type { Immutable } from "@foxglove/studio";
import type { SubscribePayload, SubscriptionPreloadType } from "@foxglove/studio-base/players/types";
export declare function pathToSubscribePayload(path: Immutable<MessagePath>, preloadType: SubscriptionPreloadType): SubscribePayload | undefined;
