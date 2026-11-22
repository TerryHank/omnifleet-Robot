export type FramePromise = {
    name: string;
    promise: Promise<void>;
};
export declare const MAX_PROMISE_TIMEOUT_TIME_MS = 5000;
export declare function pauseFrameForPromises(promises: FramePromise[]): Promise<void>;
