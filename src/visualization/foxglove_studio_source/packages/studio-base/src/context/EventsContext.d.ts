/// <reference types="react" />
import { AsyncState } from "react-use/lib/useAsyncFn";
import { StoreApi } from "zustand";
import { Time } from "@foxglove/rostime";
import { Immutable } from "@foxglove/studio";
/**
 * DataSourceEvent representings a single event within a data source.
 */
export type DataSourceEvent = {
    id: string;
    createdAt: string;
    deviceId: string;
    durationNanos: string;
    endTime: Time;
    endTimeInSeconds: number;
    metadata: Record<string, string>;
    startTime: Time;
    startTimeInSeconds: number;
    timestampNanos: string;
    updatedAt: string;
};
/**
 * Represents an event including its fractional position on the timeline.
 */
export type TimelinePositionedEvent = {
    /** The event. */
    event: DataSourceEvent;
    /** The end position of the event, as a value 0-1 relative to the timeline. */
    endPosition: number;
    /** The start position of the event, as a value 0-1 relative to the timeline. */
    startPosition: number;
    /** The time, in seconds, relative to the start of the timeline. */
    secondsSinceStart: number;
};
export type EventsStore = Immutable<{
    /** Used to signal event refreshes. */
    eventFetchCount: number;
    /** Whether events are supported for the currently loaded source. */
    eventsSupported: boolean;
    /** Fetched events for this session. */
    events: AsyncState<TimelinePositionedEvent[]>;
    /** The current event filter expression. */
    filter: string;
    /** The currently selected event, if any. */
    selectedEventId: undefined | string;
    /** The active device under which new events should be created. */
    deviceId: string | undefined;
    /** Refreshes events from api. */
    refreshEvents: () => void;
    /** Select an event by id or clear the selection. */
    selectEvent: (id: undefined | string) => void;
    /** Set the fetched events. */
    setEvents: (events: AsyncState<TimelinePositionedEvent[]>) => void;
    /** Set the flag indicating support for events. */
    setEventsSupported: (supported: boolean) => void;
    /** Update the current filter expression. */
    setFilter: (filter: string) => void;
    /** Set the active device. */
    setDeviceId: (deviceId: string | undefined) => void;
}>;
export declare const EventsContext: import("react").Context<StoreApi<{
    readonly eventFetchCount: number;
    readonly eventsSupported: boolean;
    readonly events: {
        readonly loading: boolean;
        readonly error?: undefined;
        readonly value?: undefined;
    } | {
        readonly loading: false;
        readonly error: {
            readonly name: string;
            readonly message: string;
            readonly stack?: string | undefined;
            readonly cause?: unknown;
        };
        readonly value?: undefined;
    } | {
        readonly loading: true;
        readonly error?: {
            readonly name: string;
            readonly message: string;
            readonly stack?: string | undefined;
            readonly cause?: unknown;
        } | undefined;
        readonly value?: readonly {
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
        }[] | undefined;
    } | {
        readonly loading: false;
        readonly error?: undefined;
        readonly value: readonly {
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
        }[];
    };
    readonly filter: string;
    readonly selectedEventId: undefined | string;
    readonly deviceId: string | undefined;
    readonly refreshEvents: () => void;
    readonly selectEvent: (id: undefined | string) => void;
    readonly setEvents: (events: AsyncState<TimelinePositionedEvent[]>) => void;
    readonly setEventsSupported: (supported: boolean) => void;
    readonly setFilter: (filter: string) => void;
    readonly setDeviceId: (deviceId: string | undefined) => void;
}> | undefined>;
export declare function useEvents<T>(selector: (store: EventsStore) => T): T;
