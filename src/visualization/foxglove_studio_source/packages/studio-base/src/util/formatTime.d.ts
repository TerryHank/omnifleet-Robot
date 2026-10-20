import { Time } from "@foxglove/rostime";
import { TimeDisplayMethod } from "@foxglove/studio-base/types/panels";
export declare function format(stamp: Time, timezone?: string): string;
export declare function formatDate(stamp: Time, timezone?: string): string;
export declare function formatTime(stamp: Time, timezone?: string): string;
export declare function formatDuration(stamp: Time): string;
export declare function parseTimeStr(str: string, timezone?: string): Time | undefined;
export declare const getValidatedTimeAndMethodFromString: ({ text, timezone, }: {
    text?: string | undefined;
    timezone?: string | undefined;
}) => {
    time?: Time;
    method: TimeDisplayMethod;
} | undefined;
