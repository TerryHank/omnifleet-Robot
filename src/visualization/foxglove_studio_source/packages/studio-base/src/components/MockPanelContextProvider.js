import { jsx as _jsx } from "react/jsx-runtime";
import PanelContext from "@foxglove/studio-base/components/PanelContext";
const DEFAULT_MOCK_PANEL_CONTEXT = {
    type: "foo",
    id: "bar",
    title: "Foo Panel",
    config: {},
    saveConfig: () => { },
    updatePanelConfigs: () => { },
    openSiblingPanel: () => { },
    replacePanel: () => { },
    enterFullscreen: () => { },
    exitFullscreen: () => { },
    setHasFullscreenDescendant: () => { },
    isFullscreen: false,
    connectToolbarDragHandle: () => { },
    setMessagePathDropConfig: () => { },
};
function MockPanelContextProvider({ children, ...rest }) {
    return (_jsx(PanelContext.Provider, { value: {
            ...DEFAULT_MOCK_PANEL_CONTEXT,
            ...rest,
        }, children: children }));
}
export default MockPanelContextProvider;
