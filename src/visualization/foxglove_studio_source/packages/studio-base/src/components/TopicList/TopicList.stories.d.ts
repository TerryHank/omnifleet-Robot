/// <reference types="react" />
import { StoryObj } from "@storybook/react";
import MockMessagePipelineProvider from "@foxglove/studio-base/components/MessagePipeline/MockMessagePipelineProvider";
declare const _default: import("@storybook/types").ComponentAnnotations<import("@storybook/react/dist/types-0fc72a6d").R, import("@foxglove/studio-base/components/MessagePipeline/MockMessagePipelineProvider").MockMessagePipelineProps & {
    children?: import("react").ReactNode;
}>;
export default _default;
type Story = StoryObj<typeof MockMessagePipelineProvider>;
export declare const Default: Story;
export declare const Empty: Story;
export declare const EmptyChinese: Story;
export declare const EmptyJapanese: Story;
export declare const ContextMenuSingleTopic: Story;
export declare const ContextMenuMultipleTopics: Story;
export declare const ContextMenuSinglePath: Story;
export declare const ContextMenuMultiplePaths: Story;
export declare const FilterByTopicName: Story;
export declare const FilterBySchemaName: Story;
export declare const FilterByFieldName: Story;
export declare const FilterByMessagePath: Story;
export declare const FilterTextCleared: Story;
export declare const NoResults: Story;
export declare const NoResultsChinese: Story;
export declare const NoResultsJapanese: Story;
