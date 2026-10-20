/// <reference types="react" />
type Vec3Props = {
    disabled?: boolean;
    onChange: (value: undefined | [undefined | number, undefined | number, undefined | number]) => void;
    precision?: number;
    readOnly?: boolean;
    step?: number;
    placeholder?: readonly [undefined | string, undefined | string, undefined | string];
    value: undefined | readonly [undefined | number, undefined | number, undefined | number];
    min?: number;
    max?: number;
};
export declare function Vec3Input(props: Vec3Props): JSX.Element;
export {};
