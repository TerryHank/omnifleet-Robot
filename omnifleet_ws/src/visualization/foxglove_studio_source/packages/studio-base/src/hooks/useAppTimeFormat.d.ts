import { Time } from "@foxglove/studio";
import { TimeDisplayMethod } from "@foxglove/studio-base/types/panels";
export interface IAppTimeFormat {
    formatDate: (date: Time) => string;
    formatTime: (stamp: Time) => string;
    formatDuration: (duration: Time) => string;
    timeFormat: TimeDisplayMethod;
    setTimeFormat: (format: TimeDisplayMethod) => Promise<void>;
    timeZone: string | undefined;
}
export declare function useAppTimeFormat(): IAppTimeFormat;
