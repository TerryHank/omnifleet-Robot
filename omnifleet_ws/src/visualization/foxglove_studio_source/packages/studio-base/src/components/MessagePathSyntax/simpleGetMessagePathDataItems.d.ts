import { MessagePath } from "@foxglove/message-path";
import { Immutable } from "@foxglove/studio";
import { MessageEvent } from "@foxglove/studio-base/players/types";
/**
 * Execute the given message path to extract item(s) from the message.
 */
export declare function simpleGetMessagePathDataItems(message: Immutable<MessageEvent>, filledInPath: Immutable<MessagePath>): unknown[];
