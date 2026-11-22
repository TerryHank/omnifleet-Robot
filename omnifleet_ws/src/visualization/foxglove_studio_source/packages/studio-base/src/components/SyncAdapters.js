import { Fragment as _Fragment, jsxs as _jsxs, jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { useMemo } from "react";
import { CurrentLayoutLocalStorageSyncAdapter } from "@foxglove/studio-base/components/CurrentLayoutLocalStorageSyncAdapter";
import { URLStateSyncAdapter } from "@foxglove/studio-base/components/URLStateSyncAdapter";
import { useAppContext } from "@foxglove/studio-base/context/AppContext";
export function SyncAdapters() {
    // Sync adapters from app context override any local sync adapters
    const { syncAdapters } = useAppContext();
    return useMemo(() => {
        if (syncAdapters) {
            return _jsxs(_Fragment, { children: [...syncAdapters] });
        }
        return (_jsxs(_Fragment, { children: [_jsx(URLStateSyncAdapter, {}), _jsx(CurrentLayoutLocalStorageSyncAdapter, {})] }));
    }, [syncAdapters]);
}
