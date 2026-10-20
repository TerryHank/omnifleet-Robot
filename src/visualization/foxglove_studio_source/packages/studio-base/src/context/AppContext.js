// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { createContext, useContext } from "react";
export const INJECTED_FEATURE_KEYS = {
    customSceneExtensions: "ThreeDeeRender.customSceneExtensions",
};
const AppContext = createContext({
    // Default wrapPlayer is a no-op and is a pass-through of the provided child player
    wrapPlayer: (child) => child,
});
AppContext.displayName = "AppContext";
export function useAppContext() {
    return useContext(AppContext);
}
export { AppContext };
