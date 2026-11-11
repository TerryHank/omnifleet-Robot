import { StoryObj } from "@storybook/react";
import { TabPanelConfig } from "@foxglove/studio-base/src/types/layouts";
import { Fixture } from "@foxglove/studio-base/stories/PanelSetup";
type StoryArgs = {
    disableMockCatalog?: boolean;
    fixture?: Fixture;
    showPanelList?: boolean;
    overrideConfig?: TabPanelConfig;
};
declare const _default: {
    title: string;
    parameters: {
        chromatic: {
            delay: number;
        };
        colorScheme: string;
    };
    decorators: ((Wrapped: import("@storybook/types").PartialStoryFn<import("@storybook/react/dist/types-0fc72a6d").R, {
        disableMockCatalog?: boolean | undefined;
        fixture?: Fixture | undefined;
        showPanelList?: boolean | undefined;
        overrideConfig?: TabPanelConfig | undefined;
    }>, ctx: import("@storybook/types").StoryContext<import("@storybook/react/dist/types-0fc72a6d").R, {
        disableMockCatalog?: boolean | undefined;
        fixture?: Fixture | undefined;
        showPanelList?: boolean | undefined;
        overrideConfig?: TabPanelConfig | undefined;
    }>) => import("react/jsx-runtime").JSX.Element)[];
};
export default _default;
type Story = StoryObj<StoryArgs>;
export declare const Default: Story;
export declare const ShowingPanelList: Story;
export declare const ShowingPanelListLight: Story;
export declare const PickingAPanelFromThePanelListCreatesANewTabIfThereAreNone: Story;
export declare const PickingAPanelFromThePanelListUpdatesTheTabsLayout: Story;
export declare const DraggingAPanelFromThePanelListUpdatesTheTabsLayout: Story;
export declare const DraggingAPanelFromThePanelListCreatesANewTabIfThereAreNone: Story;
export declare const WithChosenActiveTab: Story;
export declare const AddTab: Story;
export declare const RemoveTab: Story;
export declare const ReorderTabsWithinTabPanelByDroppingOnTab: Story;
export declare const MoveTabToDifferentTabPanel: Story;
export declare const PreventDraggingSelectedParentTabIntoChildTabPanel: Story;
export declare const DraggingAndDroppingANestedTabPanelDoesNotRemoveAnyTabs: Story;
export declare const SupportsDraggingBetweenTabsAnywhereInTheLayout: Story;
export declare const DraggingOntoTabRootDoesNotReplaceTabContents: Story;
