/// <reference types="react" />
import { IconButtonProps } from "@mui/material";
type Props = {
    icon: React.ReactNode;
    activeIcon?: React.ReactNode;
    color?: IconButtonProps["color"];
    activeColor?: IconButtonProps["color"];
} & Omit<IconButtonProps, "children" | "color">;
declare const HoverableIconButton: import("react").ForwardRefExoticComponent<Omit<Props, "ref"> & import("react").RefAttributes<HTMLButtonElement>>;
export default HoverableIconButton;
