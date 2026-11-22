import { StoreApi } from "zustand";
import { IStudioLogsSettings } from "@foxglove/studio-base/context/StudioLogsSettingsContext";
import { LocalStorageSaveState } from "./types";
declare function createStudioLogsSettingsStore(initialState?: LocalStorageSaveState): StoreApi<IStudioLogsSettings>;
export { createStudioLogsSettingsStore };
