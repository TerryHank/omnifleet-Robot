/// <reference types="react" />
type Vec2Props = {
    disabled?: boolean;
    onChange: (value: undefined | [undefined | number, undefined | number]) => void;
    precision?: number;
    readOnly?: boolean;
    step?: number;
    placeholder?: readonly [undefined | string, undefined | string];
    value: undefined | readonly [undefined | number, undefined | number];
    min?: number;
    max?: number;
};
export declare function Vec2Input(props: Vec2Props): JSX.Element;
export {};
