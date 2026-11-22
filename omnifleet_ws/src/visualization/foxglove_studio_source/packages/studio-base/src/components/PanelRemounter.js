import { jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { Fragment, useCallback } from "react";
import { usePanelStateStore, } from "@foxglove/studio-base/context/PanelStateContext";
/**
 * Wrapper component used to force-remount the panel when key properties like the tabId
 * or settings sequence number change.
 */
export function PanelRemounter({ children, id, tabId, }) {
    const selector = useCallback((store) => store.sequenceNumbers[id] ?? 0, [id]);
    const sequenceNumber = usePanelStateStore(selector);
    return _jsx(Fragment, { children: children }, `${id}${tabId ?? ""}${sequenceNumber}`);
}
