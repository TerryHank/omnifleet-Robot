// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { createContext, useContext } from "react";
const PanelCatalogContext = createContext(undefined);
PanelCatalogContext.displayName = "PanelCatalogContext";
export function usePanelCatalog() {
    const panelCatalog = useContext(PanelCatalogContext);
    if (!panelCatalog) {
        throw new Error("A PanelCatalogContext provider is required to usePanelCatalog");
    }
    return panelCatalog;
}
export default PanelCatalogContext;
