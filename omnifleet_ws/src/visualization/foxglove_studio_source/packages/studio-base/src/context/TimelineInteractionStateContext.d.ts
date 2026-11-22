/// <reference types="react" />
import { StoreApi } from "zustand";
import { Immutable } from "@foxglove/studio";
import { TimelinePositionedEvent } from "@foxglove/studio-base/context/EventsContext";
import type { HoverValue } from "@foxglove/studio-base/types/hoverValue";
/**
 * Represents the global bounds to which synced plots conform, including the id of the
 * component that set those bounds.
 */
export type SyncBounds = {
    min: number;
    max: number;
    sourceId: string;
    userInteraction: boolean;
};
/**
 * The TimelineInteractionStateStore manages state related to dynamic user interactions with data in the app.
 * Things like the hovered time value and global bounds for plots are managed here.
 */
export type TimelineInteractionStateStore = Immutable<{
    /** The events overlapping the current hover time, if any. */
    eventsAtHoverValue: Record<string, TimelinePositionedEvent>;
    /** Shared time bounds for synced plots, if any. */
    globalBounds: undefined | SyncBounds;
    /** The event directly hovered over by the user, if any. */
    hoveredEvent: undefined | TimelinePositionedEvent;
    /** The point in time hovered over by the user. */
    hoverValue: undefined | HoverValue;
    /** Clears the current hover value. */
    clearHoverValue: (componentId: string) => void;
    /** Sets the events overlapping the current hover time. */
    setEventsAtHoverValue: (events: TimelinePositionedEvent[]) => void;
    /** Sets new global bounds. */
    setGlobalBounds: (newBounds: undefined | SyncBounds | ((oldValue: undefined | SyncBounds) => undefined | SyncBounds)) => void;
    /** Sets or clears the directly hovered event. */
    setHoveredEvent: (hoveredEvent: undefined | TimelinePositionedEvent) => void;
    /** Sets the new hover value. */
    setHoverValue: (value: HoverValue) => void;
}>;
export declare const TimelineInteractionStateContext: import("react").Context<StoreApi<{
    readonly eventsAtHoverValue: {
        readonly [x: string]: {
            readonly event: {
                readonly id: string;
                readonly createdAt: string;
                readonly deviceId: string;
                readonly durationNanos: string;
                readonly endTime: {
                    readonly sec: number;
                    readonly nsec: number;
                };
                readonly endTimeInSeconds: number;
                readonly metadata: {
                    readonly [x: string]: string;
                };
                readonly startTime: {
                    readonly sec: number;
                    readonly nsec: number;
                };
                readonly startTimeInSeconds: number;
                readonly timestampNanos: string;
                readonly updatedAt: string;
            };
            readonly endPosition: number;
            readonly startPosition: number;
            readonly secondsSinceStart: number;
        };
    };
    readonly globalBounds: {
        readonly min: number;
        readonly max: number;
        readonly sourceId: string;
        readonly userInteraction: boolean;
    } | undefined;
    readonly hoveredEvent: {
        readonly event: {
            readonly id: string;
            readonly createdAt: string;
            readonly deviceId: string;
            readonly durationNanos: string;
            readonly endTime: {
                readonly sec: number;
                readonly nsec: number;
            };
            readonly endTimeInSeconds: number;
            readonly metadata: {
                readonly [x: string]: string;
            };
            readonly startTime: {
                readonly sec: number;
                readonly nsec: number;
            };
            readonly startTimeInSeconds: number;
            readonly timestampNanos: string;
            readonly updatedAt: string;
        };
        readonly endPosition: number;
        readonly startPosition: number;
        readonly secondsSinceStart: number;
    } | undefined;
    readonly hoverValue: {
        readonly value: number;
        readonly componentId: string;
        readonly type: "PLAYBACK_SECONDS" | "OTHER";
    } | undefined;
    readonly clearHoverValue: (componentId: string) => void;
    readonly setEventsAtHoverValue: (events: TimelinePositionedEvent[]) => void;
    readonly setGlobalBounds: (newBounds: SyncBounds | ((oldValue: undefined | SyncBounds) => undefined | SyncBounds) | undefined) => void;
    readonly setHoveredEvent: (hoveredEvent: undefined | TimelinePositionedEvent) => void;
    readonly setHoverValue: (value: HoverValue) => void;
}> | undefined>;
export declare function useClearHoverValue(): TimelineInteractionStateStore["clearHoverValue"];
export declare function useSetHoverValue(): TimelineInteractionStateStore["setHoverValue"];
/**
 * Select the current hover value.
 *
 * By default this hook will return the latest hover value regardless of origin. Use options to
 * control when hover value updates cause the hook to return the updated value.
 *
 * @param componentId allow updates from hover values to those matching this componentId. If undefined, any component's hover values are returned.
 * @param disableUpdates disable any updates regardless of origin. If set the hook will not update with hover values even if other options would cause a match.
 * @param isPlaybackSeconds allow updates from hover values for PLAYBACK_SECONDS
 */
export declare function useHoverValue(opt?: {
    componentId?: string;
    disableUpdates?: boolean;
    isPlaybackSeconds?: boolean;
}): HoverValue | undefined;
/**
 * This hook wraps all access to the interaction state store. Pass selectors
 * to access parts of the store.
 */
export declare function useTimelineInteractionState<T>(selector: (store: TimelineInteractionStateStore) => T): T;
