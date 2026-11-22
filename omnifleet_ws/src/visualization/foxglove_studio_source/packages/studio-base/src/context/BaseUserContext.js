// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { createContext, useContext } from "react";
const BaseUserContext = createContext({
    currentUserType: "unauthenticated",
});
BaseUserContext.displayName = "BaseUserContext";
export function useCurrentUser() {
    return useContext(BaseUserContext);
}
export default BaseUserContext;
