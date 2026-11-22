/// <reference types="react" />
import { StoryObj } from "@storybook/react";
declare function MessagePathInputStory(props: {
    path: string;
    prioritizedDatatype?: string;
    validTypes?: string[];
    heavy?: boolean;
}): JSX.Element;
declare const _default: {
    title: string;
    parameters: {
        colorScheme: string;
    };
};
export default _default;
type MsgPathInputStoryObj = StoryObj<typeof MessagePathInputStory>;
export declare const PathWithHeaderFields: MsgPathInputStoryObj;
export declare const AutocompleteTopics: MsgPathInputStoryObj;
export declare const AutocompleteScalarFromTopicAndEmptyPath: MsgPathInputStoryObj;
export declare const AutocompleteScalarFromTopic: MsgPathInputStoryObj;
export declare const AutocompleteScalarFromFullTopic: MsgPathInputStoryObj;
export declare const AutocompleteWithFilterAndArraySuggestions: MsgPathInputStoryObj;
export declare const AutocompleteMessagePath: MsgPathInputStoryObj;
export declare const AutocompleteMessagePathLight: MsgPathInputStoryObj;
export declare const AutocompleteFilter: MsgPathInputStoryObj;
export declare const AutocompleteTopLevelFilter: MsgPathInputStoryObj;
export declare const AutocompleteForGlobalVariablesVariables: MsgPathInputStoryObj;
export declare const PathWithValidGlobalVariablesVariable: MsgPathInputStoryObj;
export declare const PathWithInvalidGlobalVariablesVariable: MsgPathInputStoryObj;
export declare const PathWithIncorrectlyPrefixedGlobalVariablesVariable: MsgPathInputStoryObj;
export declare const AutocompleteForPathWithGlobalVariablesVariableInSliceSingleIdx: MsgPathInputStoryObj;
export declare const AutocompleteForPathWithGlobalVariablesVariableInSliceStartIdx: MsgPathInputStoryObj;
export declare const AutocompleteForPathWithGlobalVariablesVariableInSliceEndIdx: MsgPathInputStoryObj;
export declare const AutocompleteForPathWithGlobalVariablesVariablesInSliceStartAndEndIdx: MsgPathInputStoryObj;
export declare const PathWithInvalidMathModifier: MsgPathInputStoryObj;
export declare const AutocompleteWhenPrioritizedDatatypeIsAvailable: MsgPathInputStoryObj;
export declare const AutocompleteForPathWithExistingFilter: MsgPathInputStoryObj;
export declare const AutocompleteForPathWithExistingFilterUsingAGlobalVariable: MsgPathInputStoryObj;
export declare const PerformanceTesting: MsgPathInputStoryObj;
