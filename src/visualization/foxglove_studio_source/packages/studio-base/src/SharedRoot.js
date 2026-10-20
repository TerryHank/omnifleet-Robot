import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import GlobalCss from "@foxglove/studio-base/components/GlobalCss";
import { SharedRootContext, } from "@foxglove/studio-base/context/SharedRootContext";
import { ColorSchemeThemeProvider } from "./components/ColorSchemeThemeProvider";
import CssBaseline from "./components/CssBaseline";
import ErrorBoundary from "./components/ErrorBoundary";
import AppConfigurationContext from "./context/AppConfigurationContext";
export function SharedRoot(props) {
    const { appBarLeftInset, appConfiguration, onAppBarDoubleClick, AppBarComponent, children, customWindowControlProps, dataSources, deepLinks, enableGlobalCss = false, enableLaunchPreferenceScreen, extraProviders, } = props;
    return (_jsx(AppConfigurationContext.Provider, { value: appConfiguration, children: _jsxs(ColorSchemeThemeProvider, { children: [enableGlobalCss && _jsx(GlobalCss, {}), _jsx(CssBaseline, { children: _jsx(ErrorBoundary, { children: _jsx(SharedRootContext.Provider, { value: {
                                appBarLeftInset,
                                AppBarComponent,
                                appConfiguration,
                                customWindowControlProps,
                                dataSources,
                                deepLinks,
                                enableLaunchPreferenceScreen,
                                extraProviders,
                                onAppBarDoubleClick,
                            }, children: children }) }) })] }) }));
}
