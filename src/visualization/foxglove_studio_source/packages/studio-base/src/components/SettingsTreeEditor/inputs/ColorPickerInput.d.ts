/// <reference types="react" />
type ColorPickerInputProps = {
    alphaType: "none" | "alpha";
    disabled?: boolean;
    value: undefined | string;
    onChange: (value: undefined | string) => void;
    placeholder?: string;
    readOnly?: boolean;
    hideClearButton?: boolean;
};
export declare function ColorPickerInput(props: ColorPickerInputProps): JSX.Element;
export {};
