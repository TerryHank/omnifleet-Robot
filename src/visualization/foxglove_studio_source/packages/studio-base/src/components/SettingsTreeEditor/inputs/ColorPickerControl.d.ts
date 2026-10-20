/// <reference types="react" />
type ColorPickerProps = {
    value: undefined | string;
    alphaType: "none" | "alpha";
    onChange: (value: string) => void;
};
type ColorPickerInputProps = {
    onEnterKey?: () => void;
    swatchColor: string;
    updatePrefixedColor: (newValue: string) => void;
    editedValueIsInvalid: boolean;
    editedValue: string;
    updateEditedValue: (newValue: string) => void;
    onInputBlur: () => void;
} & Omit<ColorPickerProps, "value">;
export declare function ColorPickerControl(props: ColorPickerInputProps): JSX.Element;
export declare function useColorPickerControl(props: ColorPickerProps): {
    alphaType: "none" | "alpha";
    swatchColor: string;
    displayValue: string | undefined;
    updatePrefixedColor: (newValue: string) => void;
    editedValueIsInvalid: boolean;
    editedValue: string;
    updateEditedValue: (newValue: string) => void;
    onInputBlur: () => void;
    onChange: (value: string) => void;
};
export {};
