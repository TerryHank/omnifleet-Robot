import { ButtonProps, IconButtonProps } from "@mui/material";
import { PropsWithChildren } from "react";
declare function CopyButtonComponent(props: PropsWithChildren<{
    getText: () => string;
    size?: "small" | "medium" | "large";
    iconSize?: "small" | "medium" | "large";
    color?: ButtonProps["color"];
    className?: string;
    edge?: IconButtonProps["edge"];
}>): JSX.Element;
declare const _default: import("react").MemoExoticComponent<typeof CopyButtonComponent>;
export default _default;
