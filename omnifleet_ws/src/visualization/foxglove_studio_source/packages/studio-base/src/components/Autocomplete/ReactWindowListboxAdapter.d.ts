/// <reference types="react" />
import { AutocompleteRenderOptionState } from "@mui/material";
import { FzfResultItem } from "fzf";
/** The type of each child component from the Autocomplete */
export type ListboxAdapterChild = [
    React.HTMLAttributes<HTMLLIElement>,
    FzfResultItem,
    AutocompleteRenderOptionState
];
/**
 * React-window adapter to use a virtualized list as the autocomplete ListboxComponent to support
 * lists with thousands of elements without rendering all of them to the DOM.
 *
 * From the Autocomplete parent it receives a list of children (which must conform to the
 * ListboxAdapterChild type), and props to apply to the outer listbox element.
 */
export declare const ReactWindowListboxAdapter: import("react").ForwardRefExoticComponent<import("react").HTMLAttributes<HTMLElement> & import("react").RefAttributes<HTMLDivElement>>;
