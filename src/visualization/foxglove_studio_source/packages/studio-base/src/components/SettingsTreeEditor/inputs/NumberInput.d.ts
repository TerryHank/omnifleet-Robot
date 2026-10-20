import { TextFieldProps } from "@mui/material";
import { ReactNode } from "react";
export declare function NumberInput(props: {
    iconUp?: ReactNode;
    iconDown?: ReactNode;
    max?: number;
    min?: number;
    precision?: number;
    readOnly?: boolean;
    step?: number;
    value?: number;
    onChange: (value: undefined | number) => void;
} & Omit<TextFieldProps, "onChange">): JSX.Element;
