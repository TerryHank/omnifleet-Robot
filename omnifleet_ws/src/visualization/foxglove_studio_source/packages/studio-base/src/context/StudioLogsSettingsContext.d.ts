/// <reference types="react" />
import { StoreApi } from "zustand";
import { LogLevel } from "@foxglove/log";
type StudioLogConfigChannel = {
    name: string;
    enabled: boolean;
};
interface IStudioLogsSettings {
    readonly globalLevel: LogLevel;
    readonly channels: ReadonlyArray<{
        name: string;
        enabled: boolean;
    }>;
    enableChannel(name: string): void;
    disableChannel(name: string): void;
    enablePrefix(prefix: string): void;
    disablePrefix(prefix: string): void;
    setGlobalLevel(level: LogLevel): void;
}
declare const StudioLogsSettingsContext: import("react").Context<StoreApi<IStudioLogsSettings> | undefined>;
declare function useStudioLogsSettings(): IStudioLogsSettings;
export { StudioLogsSettingsContext, useStudioLogsSettings };
export type { IStudioLogsSettings, StudioLogConfigChannel };
