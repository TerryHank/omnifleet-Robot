import { jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { StrictMode, useMemo } from "react";
import ReactDOM from "react-dom";
import { useCrash } from "@foxglove/hooks";
import { CaptureErrorBoundary } from "@foxglove/studio-base/components/CaptureErrorBoundary";
import { ForwardAnalyticsContextProvider, useForwardAnalytics, } from "@foxglove/studio-base/components/ForwardAnalyticsContextProvider";
import Panel from "@foxglove/studio-base/components/Panel";
import { PanelExtensionAdapter, } from "@foxglove/studio-base/components/PanelExtensionAdapter";
import { INJECTED_FEATURE_KEYS, useAppContext } from "@foxglove/studio-base/context/AppContext";
import { ThreeDeeRender } from "./ThreeDeeRender";
function initPanel(args, context) {
    const { crash, forwardedAnalytics, interfaceMode, testOptions, customSceneExtensions } = args;
    // eslint-disable-next-line react/no-deprecated
    ReactDOM.render(_jsx(StrictMode, { children: _jsx(CaptureErrorBoundary, { onError: crash, children: _jsx(ForwardAnalyticsContextProvider, { forwardedAnalytics: forwardedAnalytics, children: _jsx(ThreeDeeRender, { context: context, interfaceMode: interfaceMode, testOptions: testOptions, customSceneExtensions: customSceneExtensions }) }) }) }), context.panelElement);
    return () => {
        // eslint-disable-next-line react/no-deprecated
        ReactDOM.unmountComponentAtNode(context.panelElement);
    };
}
function ThreeDeeRenderAdapter(interfaceMode, props) {
    const crash = useCrash();
    const forwardedAnalytics = useForwardAnalytics();
    const { injectedFeatures } = useAppContext();
    const customSceneExtensions = useMemo(() => {
        if (injectedFeatures == undefined) {
            return undefined;
        }
        const injectedSceneExtensions = injectedFeatures.availableFeatures[INJECTED_FEATURE_KEYS.customSceneExtensions]
            ?.customSceneExtensions;
        return injectedSceneExtensions;
    }, [injectedFeatures]);
    const boundInitPanel = useMemo(() => initPanel.bind(undefined, {
        crash,
        forwardedAnalytics,
        interfaceMode,
        testOptions: { onDownloadImage: props.onDownloadImage, debugPicking: props.debugPicking },
        customSceneExtensions,
    }), [
        crash,
        forwardedAnalytics,
        interfaceMode,
        props.onDownloadImage,
        props.debugPicking,
        customSceneExtensions,
    ]);
    return (_jsx(PanelExtensionAdapter, { config: props.config, highestSupportedConfigVersion: 1, saveConfig: props.saveConfig, initPanel: boundInitPanel }));
}
/**
 * The Image panel is a special case of the 3D panel with `interfaceMode` set to `"image"`.
 */
export const ImagePanel = Panel(Object.assign(ThreeDeeRenderAdapter.bind(undefined, "image"), {
    panelType: "Image",
    defaultConfig: {},
}));
export default Panel(Object.assign(ThreeDeeRenderAdapter.bind(undefined, "3d"), {
    panelType: "3D",
    defaultConfig: {},
}));
