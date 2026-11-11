// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { createContext } from "react";
import { useStore } from "zustand";
import { useGuaranteedContext } from "@foxglove/hooks";
const StudioLogsSettingsContext = createContext(undefined);
function useStudioLogsSettings() {
    const context = useGuaranteedContext(StudioLogsSettingsContext);
    return useStore(context);
}
export { StudioLogsSettingsContext, useStudioLogsSettings };
