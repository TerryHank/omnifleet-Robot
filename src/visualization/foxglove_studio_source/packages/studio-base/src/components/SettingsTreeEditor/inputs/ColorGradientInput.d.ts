/// <reference types="react" />
export declare function ColorGradientInput({ colors, disabled, onChange, readOnly, }: {
    colors: undefined | readonly [string, string];
    disabled?: boolean;
    onChange: (colors: [left: string, right: string]) => void;
    readOnly?: boolean;
}): JSX.Element;
