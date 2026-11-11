import { jsx as _jsx } from "react/jsx-runtime";
import VariableSliderPanel from "@foxglove/studio-base/panels/VariableSlider/index";
import PanelSetup from "@foxglove/studio-base/stories/PanelSetup";
const fixture = {
    topics: [],
    datatypes: new Map(Object.entries({
        Foo: { definitions: [] },
    })),
    frame: {},
    capabilities: [],
    globalVariables: { globalVariable: 3.5 },
};
export default {
    title: "panels/VariableSlider",
    component: VariableSliderPanel,
};
export const Example = {
    render: () => {
        return (_jsx(PanelSetup, { fixture: fixture, children: _jsx(VariableSliderPanel, {}) }));
    },
};
export const NarrowLayout = {
    render: () => {
        return (_jsx(PanelSetup, { fixture: fixture, children: _jsx("div", { style: { width: 400 }, children: _jsx(VariableSliderPanel, {}) }) }));
    },
};
export const WithSettings = {
    render: function Story() {
        return (_jsx(PanelSetup, { fixture: fixture, includeSettings: true, children: _jsx(VariableSliderPanel, {}) }));
    },
    parameters: {
        colorScheme: "light",
    },
};
