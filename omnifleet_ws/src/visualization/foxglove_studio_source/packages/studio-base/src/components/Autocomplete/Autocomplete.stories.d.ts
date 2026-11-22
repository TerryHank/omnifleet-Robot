/// <reference types="react" />
import { StoryFn, StoryObj } from "@storybook/react";
import { Autocomplete } from "./Autocomplete";
declare const _default: {
    title: string;
    component: import("react").ForwardRefExoticComponent<{
        className?: string | undefined;
        disableAutoSelect?: boolean | undefined;
        disabled?: boolean | undefined;
        filterText?: string | undefined;
        hasError?: boolean | undefined;
        inputStyle?: import("react").CSSProperties | undefined;
        items: readonly string[];
        menuStyle?: import("react").CSSProperties | undefined;
        minWidth?: number | undefined;
        onBlur?: (() => void) | undefined;
        onChange?: ((event: import("react").SyntheticEvent<Element, Event>, text: string) => void) | undefined;
        onSelect: (value: string, autocomplete: import("./Autocomplete").IAutocomplete) => void;
        placeholder?: string | undefined;
        readOnly?: boolean | undefined;
        selectOnFocus?: boolean | undefined;
        sortWhenFiltering?: boolean | undefined;
        value?: string | undefined;
        variant?: "filled" | "outlined" | "standard" | undefined;
    } & import("react").RefAttributes<import("./Autocomplete").IAutocomplete>>;
    parameters: {
        colorScheme: string;
    };
    args: {
        onSelect: () => void;
    };
    decorators: ((Story: StoryFn) => JSX.Element)[];
};
export default _default;
type Story = StoryObj<typeof Autocomplete>;
export declare const FilteringToO: Story;
export declare const FilteringToOLight: Story;
export declare const UncontrolledValue: Story;
export declare const UncontrolledValueLight: Story;
export declare const SortWhenFilteringFalse: Story;
export declare const ManyItems: Story;
export declare const LongPathInPopup: Story;
