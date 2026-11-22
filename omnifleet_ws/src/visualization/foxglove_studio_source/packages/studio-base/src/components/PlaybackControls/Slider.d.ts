import { ReactNode } from "react";
export type HoverOverEvent = {
    /** Hovered `fraction` value */
    fraction: number;
    /** Current hovered X position in client coordinates */
    clientX: number;
    /** Current hovered Y position in client coordinates */
    clientY: number;
};
type Props = {
    fraction: number | undefined;
    disabled?: boolean;
    onChange: (value: number) => void;
    onHoverOver?: (event: HoverOverEvent) => void;
    onHoverOut?: () => void;
    renderSlider?: (value?: number) => ReactNode;
};
export default function Slider(props: Props): JSX.Element;
export {};
