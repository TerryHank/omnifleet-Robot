import { PlayerState, SubscribePayload } from "@foxglove/studio-base/players/types";
import { IStateProcessor } from "./IStateProcessor";
/**
 * Overrides the process method of StateProcessor to be a passthrough.
 *
 * Useful if there is no processing to perform.
 */
export declare class NoopStateProcessor implements IStateProcessor {
    process(playerState: PlayerState): PlayerState;
    aliasSubscriptions(subs: SubscribePayload[]): SubscribePayload[];
}
