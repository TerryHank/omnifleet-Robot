/// <reference types="react" />
import { ButtonBaseProps } from "@mui/material";
type Props = {
    title: string;
    subheader?: string;
    selected: boolean;
    onClick: () => void;
} & ButtonBaseProps;
/**
 * A button that can be used in the app bar to open a dropdown menu.
 */
declare const AppBarDropdownButton: import("react").ForwardRefExoticComponent<Omit<Props, "ref"> & import("react").RefAttributes<HTMLButtonElement>>;
export { AppBarDropdownButton };
