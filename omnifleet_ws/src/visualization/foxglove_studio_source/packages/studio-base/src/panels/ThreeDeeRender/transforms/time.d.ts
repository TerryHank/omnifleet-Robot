export type Time = bigint;
export type Duration = bigint;
export declare function compareTime(a: Time, b: Time): number;
export declare function percentOf(start: Time, end: Time, target: Time): number;
export declare function interpolate(start: Time, end: Time, fraction: number): Time;
