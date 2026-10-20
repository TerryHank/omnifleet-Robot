/// <reference types="react" />
import { TimelinePositionedEvent } from "@foxglove/studio-base/context/EventsContext";
declare function EventViewComponent(params: {
    event: TimelinePositionedEvent;
    filter: string;
    formattedTime: string;
    isHovered: boolean;
    isSelected: boolean;
    onClick: (event: TimelinePositionedEvent) => void;
    onHoverStart: (event: TimelinePositionedEvent) => void;
    onHoverEnd: (event: TimelinePositionedEvent) => void;
}): JSX.Element;
export declare const EventView: import("react").MemoExoticComponent<typeof EventViewComponent>;
export {};
