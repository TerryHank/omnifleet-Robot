import { jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { createContext, useMemo } from "react";
export const MessagePathSelectionContextInternal = createContext(undefined);
/**
 * Holds state to support dragging multiple message paths at once.
 */
export function MessagePathSelectionProvider(props) {
    const value = useMemo(() => ({ getSelectedItems: props.getSelectedItems }), [props.getSelectedItems]);
    return (_jsx(MessagePathSelectionContextInternal.Provider, { value: value, children: props.children }));
}
