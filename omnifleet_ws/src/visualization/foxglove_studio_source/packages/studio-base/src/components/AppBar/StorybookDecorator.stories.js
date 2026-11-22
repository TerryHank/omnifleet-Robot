import { jsx as _jsx } from "react/jsx-runtime";
import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import MockMessagePipelineProvider from "@foxglove/studio-base/components/MessagePipeline/MockMessagePipelineProvider";
import Panel from "@foxglove/studio-base/components/Panel";
import PanelCatalogContext from "@foxglove/studio-base/context/PanelCatalogContext";
import MockCurrentLayoutProvider from "@foxglove/studio-base/providers/CurrentLayoutProvider/MockCurrentLayoutProvider";
import WorkspaceContextProvider from "@foxglove/studio-base/providers/WorkspaceContextProvider";
const SamplePanel1 = function () {
    return _jsx("div", {});
};
SamplePanel1.panelType = "sample";
SamplePanel1.defaultConfig = {};
const SamplePanel2 = function () {
    return _jsx("div", {});
};
SamplePanel2.panelType = "sample2";
SamplePanel2.defaultConfig = {};
const MockPanel1 = Panel(SamplePanel1);
const MockPanel2 = Panel(SamplePanel2);
const allPanels = [
    { title: "Regular Panel BBB", type: "Sample1", module: async () => ({ default: MockPanel1 }) },
    { title: "Regular Panel AAA", type: "Sample2", module: async () => ({ default: MockPanel2 }) },
    {
        title: "Preconfigured Panel AAA",
        type: "Sample1",
        description: "Panel description",
        module: async () => ({ default: MockPanel1 }),
        config: { text: "def" },
    },
    {
        title: "Preconfigured Panel BBB",
        type: "Sample2",
        module: async () => ({ default: MockPanel1 }),
        config: { num: 456 },
    },
];
class MockPanelCatalog {
    getPanels() {
        return allPanels;
    }
    getPanelByType(type) {
        return allPanels.find((panel) => !panel.config && panel.type === type);
    }
}
export default {
    title: "components/AppBar",
    excludeStories: ["StorybookDecorator"],
};
export function StorybookDecorator(Wrapped) {
    return (_jsx(DndProvider, { backend: HTML5Backend, children: _jsx(WorkspaceContextProvider, { children: _jsx(PanelCatalogContext.Provider, { value: new MockPanelCatalog(), children: _jsx(MockCurrentLayoutProvider, { children: _jsx(MockMessagePipelineProvider, { children: _jsx(Wrapped, {}) }) }) }) }) }));
}
