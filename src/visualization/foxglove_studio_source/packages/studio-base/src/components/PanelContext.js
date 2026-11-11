// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
//
// This file incorporates work covered by the following copyright and
// permission notice:
//
//   Copyright 2018-2021 Cruise LLC
//
//   This source code is licensed under the Apache License, Version 2.0,
//   found at http://www.apache.org/licenses/LICENSE-2.0
//   You may not use this file except in compliance with the License.
// Context used for components to know which panel they are inside
const PanelContext = React.createContext(undefined);
PanelContext.displayName = "PanelContext";
export function usePanelContext() {
    const context = React.useContext(PanelContext);
    if (!context) {
        throw new Error("Tried to use PanelContext outside a <PanelContext.Provider />");
    }
    return context;
}
export default PanelContext;
