// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { createContext, useContext } from "react";
const PlayerSelectionContext = createContext({
    selectSource: () => { },
    selectRecent: () => { },
    availableSources: [],
    recentSources: [],
});
PlayerSelectionContext.displayName = "PlayerSelectionContext";
export function usePlayerSelection() {
    return useContext(PlayerSelectionContext);
}
export default PlayerSelectionContext;
