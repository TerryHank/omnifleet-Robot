import { jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { StrictMode, useMemo } from "react";
import ReactDOM from "react-dom";
import { useCrash } from "@foxglove/hooks";
import { CaptureErrorBoundary } from "@foxglove/studio-base/components/CaptureErrorBoundary";
import Panel from "@foxglove/studio-base/components/Panel";
import { PanelExtensionAdapter } from "@foxglove/studio-base/components/PanelExtensionAdapter";
import ThemeProvider from "@foxglove/studio-base/theme/ThemeProvider";
import { Indicator } from "./Indicator";
function initPanel(crash, context) {
    // eslint-disable-next-line react/no-deprecated
    ReactDOM.render(_jsx(StrictMode, { children: _jsx(CaptureErrorBoundary, { onError: crash, children: _jsx(ThemeProvider, { isDark: true, children: _jsx(Indicator, { context: context }) }) }) }), context.panelElement);
    return () => {
        // eslint-disable-next-line react/no-deprecated
        ReactDOM.unmountComponentAtNode(context.panelElement);
    };
}
function IndicatorLightPanelAdapter(props) {
    const crash = useCrash();
    const boundInitPanel = useMemo(() => initPanel.bind(undefined, crash), [crash]);
    return (_jsx(PanelExtensionAdapter, { config: props.config, saveConfig: props.saveConfig, initPanel: boundInitPanel, highestSupportedConfigVersion: 1 }));
}
IndicatorLightPanelAdapter.panelType = "Indicator";
IndicatorLightPanelAdapter.defaultConfig = {};
export default Panel(IndicatorLightPanelAdapter);
