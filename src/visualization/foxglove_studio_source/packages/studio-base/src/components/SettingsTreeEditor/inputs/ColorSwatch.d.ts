/// <reference types="react" />
type ColorSwatchProps = {
    color: string;
    size?: "small" | "medium" | "large";
} & React.HTMLAttributes<HTMLDivElement>;
export declare function ColorSwatch(props: ColorSwatchProps): JSX.Element;
export {};
