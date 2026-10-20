/// <reference types="react" />
export type CustomWindowControlsProps = {
    showCustomWindowControls?: boolean;
    isMaximized?: boolean;
    initialZoomFactor?: number;
    onMinimizeWindow?: () => void;
    onMaximizeWindow?: () => void;
    onUnmaximizeWindow?: () => void;
    onCloseWindow?: () => void;
};
export declare function CustomWindowControls({ isMaximized, onMinimizeWindow, onMaximizeWindow, onUnmaximizeWindow, onCloseWindow, }: Omit<CustomWindowControlsProps, "showCustomWindowControls">): JSX.Element;
