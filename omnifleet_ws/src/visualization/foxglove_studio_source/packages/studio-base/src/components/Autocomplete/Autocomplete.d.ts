import { TextFieldProps } from "@mui/material";
import * as React from "react";
import { CSSProperties } from "react";
type AutocompleteProps = {
    className?: string;
    disableAutoSelect?: boolean;
    disabled?: boolean;
    filterText?: string;
    hasError?: boolean;
    inputStyle?: CSSProperties;
    items: readonly string[];
    menuStyle?: CSSProperties;
    minWidth?: number;
    onBlur?: () => void;
    onChange?: (event: React.SyntheticEvent, text: string) => void;
    onSelect: (value: string, autocomplete: IAutocomplete) => void;
    placeholder?: string;
    readOnly?: boolean;
    selectOnFocus?: boolean;
    sortWhenFiltering?: boolean;
    value?: string;
    variant?: TextFieldProps["variant"];
};
export interface IAutocomplete {
    setSelectionRange(selectionStart: number, selectionEnd: number): void;
    focus(): void;
    blur(): void;
}
/**
 * <Autocomplete> is a Studio-specific wrapper of MUI autocomplete with support
 * for things like multiple autocompletes that seamlessly transition into each
 * other, e.g. when building more complex strings like in the Plot panel.
 */
export declare const Autocomplete: React.ForwardRefExoticComponent<AutocompleteProps & React.RefAttributes<IAutocomplete>>;
export {};
