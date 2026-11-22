import { Immutable as Im } from "@foxglove/studio";
import { PlayerProblem, PlayerState, SubscribePayload } from "@foxglove/studio-base/players/types";
import { IStateProcessor } from "./IStateProcessor";
export type TopicAliasMap = Map<string, string[]>;
/**
 * StateProcessor implements IStateProcessor to apply topic aliases to player state and subscriptions.
 *
 * Note: it uses a set of memoized members to keep referential equality for the output player state
 * when the input is unchanged. This is important for downstream consumers which rely on referential
 * equality to detect changes and to avoid doing work when there are no changes.
 */
export declare class AliasingStateProcessor implements IStateProcessor {
    #private;
    constructor(mapping: Im<TopicAliasMap>, problems?: PlayerProblem[]);
    /**
     * Aliases topics in a player state to a new player state with all topic name aliases
     * applied.
     *
     * Subscriptions are aliased to include the mapped and unmapped topics.
     */
    process(playerState: PlayerState, subscriptions: Im<SubscribePayload[]>): PlayerState;
    aliasSubscriptions: ((subcriptions: SubscribePayload[]) => SubscribePayload[]) & {
        clear(): void;
    };
}
