import { jsx as _jsx, Fragment as _Fragment, jsxs as _jsxs } from "react/jsx-runtime";
import { userEvent } from "@storybook/testing-library";
import { useCallback } from "react";
import { v4 as uuid } from "uuid";
import Panel from "@foxglove/studio-base/components/Panel";
import { PanelContextMenu, } from "@foxglove/studio-base/components/PanelContextMenu";
import PanelToolbar from "@foxglove/studio-base/components/PanelToolbar";
import PanelSetup from "@foxglove/studio-base/stories/PanelSetup";
export default {
    title: "components/PanelContextMenu",
};
const DUMMY_CLASS = uuid();
function DummyPanel() {
    const getItems = useCallback(() => [
        { type: "item", label: "Download Image", onclick: () => undefined },
        { type: "item", label: "Flip Horizontal", onclick: () => undefined },
        { type: "item", label: "Flip Vertical", onclick: () => undefined },
    ], []);
    return (_jsxs(_Fragment, { children: [_jsx(PanelToolbar, {}), _jsx(PanelContextMenu, { getItems: getItems }), _jsx("div", { className: DUMMY_CLASS, style: {
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    width: "100%",
                    height: "100%",
                }, children: _jsx("p", { children: "Panel Context Menu" }) })] }));
}
const Dummy = Panel(Object.assign(DummyPanel, {
    panelType: "Dummy",
    defaultConfig: {},
}));
export const Default = {
    render: () => {
        return (_jsx(PanelSetup, { children: _jsx(Dummy, {}) }));
    },
    play: async () => {
        for (const target of document.getElementsByClassName(DUMMY_CLASS)) {
            const rect = target.getBoundingClientRect();
            await userEvent.pointer({
                target,
                keys: "[MouseRight]",
                coords: {
                    clientX: rect.x + 100,
                    clientY: rect.y + 100,
                },
            });
        }
    },
};
