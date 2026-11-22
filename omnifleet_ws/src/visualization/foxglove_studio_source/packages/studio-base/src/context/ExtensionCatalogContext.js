// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { createContext, useContext } from "react";
import { createStore, useStore } from "zustand";
export const ExtensionCatalogContext = createContext(createStore(() => ({
    installExtension: async () => await Promise.reject("Unsupported"),
    installedExtensions: [],
    installedPanels: {},
    installedMessageConverters: [],
    installedTopicAliasFunctions: [],
})));
export function useExtensionCatalog(selector) {
    const context = useContext(ExtensionCatalogContext);
    return useStore(context, selector);
}
