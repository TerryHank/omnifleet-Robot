// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { createContext, useContext } from "react";
import NullAnalytics from "@foxglove/studio-base/services/NullAnalytics";
const AnalyticsContext = createContext(new NullAnalytics());
AnalyticsContext.displayName = "AnalyticsContext";
export function useAnalytics() {
    return useContext(AnalyticsContext);
}
export default AnalyticsContext;
