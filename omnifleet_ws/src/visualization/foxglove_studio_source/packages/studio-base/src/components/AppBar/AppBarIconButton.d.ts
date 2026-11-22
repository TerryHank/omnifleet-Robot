/// <reference types="react" />
import { IconButtonProps } from "@mui/material";
type AppBarIconButtonProps = Omit<IconButtonProps, "title"> & {
    title?: React.ReactNode;
};
export declare const AppBarIconButton: import("react").ForwardRefExoticComponent<Omit<AppBarIconButtonProps, "ref"> & import("react").RefAttributes<HTMLButtonElement>>;
export {};
