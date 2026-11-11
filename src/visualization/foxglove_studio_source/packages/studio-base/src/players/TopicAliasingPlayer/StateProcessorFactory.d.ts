import { TopicAliasFunction, Immutable as Im } from "@foxglove/studio";
import { GlobalVariables } from "@foxglove/studio-base/hooks/useGlobalVariables";
import { Topic } from "@foxglove/studio-base/players/types";
import { IStateProcessor } from "./IStateProcessor";
export type TopicAliasFunctions = Array<{
    extensionId: string;
    aliasFunction: TopicAliasFunction;
}>;
export type StateFactoryInput = {
    aliasFunctions: TopicAliasFunctions;
    topics: undefined | Topic[];
    variables: GlobalVariables;
};
/**
 * StateProcessorFactory builds instances of IStateProcessor from sets of inputs.
 *
 * Its purpose is to manage idempotency and memoization of the input and output to only build a new
 * processor when a set of alias function outputs results in a semantically different output.
 */
export declare class StateProcessorFactory {
    #private;
    /**
     * Build a state processor instance from the inputs.
     *
     * Returns a StateProcessor instance from the inputs and alias functions. This builder keeps
     * track of inputs and alias function outputs and will only create a new state processor if the
     * output values change. If the output values are unchanged, the existing state processor
     * instance is returned.
     */
    buildStateProcessor(input: Im<StateFactoryInput>): IStateProcessor;
}
