/// <reference types="react" />
import { ButtonProps } from "@mui/material";
import { ReactElement } from "react-markdown/lib/react-markdown";
export type PanelOverlayProps = {
    actions?: {
        key: string;
        text: string;
        icon: ReactElement;
        onClick?: () => void;
        color?: ButtonProps["color"];
    }[];
    dropMessage?: string;
    highlightMode?: "active" | "all";
    open: boolean;
    variant?: "validDropTarget" | "invalidDropTarget" | "selected";
    onClickAway?: () => void;
};
export declare const PanelOverlay: import("react").ForwardRefExoticComponent<PanelOverlayProps & import("react").RefAttributes<HTMLDivElement>>;
