/// <reference types="react" />
import type { PlotCoordinator } from "./PlotCoordinator";
type Props = {
    coordinator?: PlotCoordinator;
    hoverComponentId: string;
    xAxisIsPlaybackTime: boolean;
};
/**
 * Display vertical bars at the currentTime & the hovered time.
 *
 * This is a separate component in order to limit the scope of what needs to re-render when time and scale change.
 */
export declare const VerticalBars: import("react").NamedExoticComponent<Props>;
export {};
