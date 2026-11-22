import { HTMLAttributes } from "react";
import { TransitionStatus } from "react-transition-group";
export declare const PANEL_ROOT_CLASS_NAME = "FoxglovePanelRoot-root";
export declare const PanelRoot: import("react").ForwardRefExoticComponent<{
    fullscreenState: TransitionStatus;
    selected: boolean;
    sourceRect: DOMRectReadOnly | undefined;
    hasFullscreenDescendant: boolean;
} & HTMLAttributes<HTMLDivElement> & {
    children?: import("react").ReactNode;
} & import("react").RefAttributes<HTMLDivElement>>;
