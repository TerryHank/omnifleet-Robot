import { MessageEvent } from "@foxglove/studio";
import { PlayerState, PlayerStateActiveData } from "@foxglove/studio-base/players/types";
export declare function mockMessage<T>(message: T, fields?: Partial<MessageEvent<T>>): MessageEvent<T>;
export declare function mockPlayerState(overrides?: Partial<PlayerState>, dataOverrides?: Partial<PlayerStateActiveData>): PlayerState;
