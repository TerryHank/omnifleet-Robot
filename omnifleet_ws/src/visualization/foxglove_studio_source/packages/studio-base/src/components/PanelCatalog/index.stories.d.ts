import { StoryFn, StoryObj } from "@storybook/react";
type Args = {
    mode?: "grid" | "list";
    inputValue?: string;
    events?: string[];
};
declare const _default: {
    title: string;
    component: ({ mode }: Args) => import("react/jsx-runtime").JSX.Element;
    parameters: {
        colorScheme: string;
    };
    decorators: ((Wrapped: StoryFn) => JSX.Element)[];
    play: ({ args }: import("@storybook/types").PlayFunctionContext<import("@storybook/react/dist/types-0fc72a6d").R, Args>) => Promise<void>;
};
export default _default;
type Story = StoryObj<Args>;
export declare const List: Story;
export declare const PanelGrid: Story;
export declare const FilteredPanelList: Story;
export declare const FilteredPanelGrid: Story;
export declare const FilteredPanelGridWithDescription: Story;
export declare const FilteredPanelListLight: Story;
export declare const NavigatingArrows: Story;
export declare const NavigatingArrowsWrap: Story;
export declare const NoResultsFirst: Story;
export declare const NoResultsLast: Story;
export declare const NoResultsAnyList: Story;
export declare const NoResultsAnyGrid: Story;
export declare const CaseInsensitiveFilter: Story;
export declare const PanelListChinese: Story;
export declare const PanelListJapanese: Story;
export declare const NoResultsChinese: Story;
export declare const NoResultsJapanese: Story;
