import { jsx as _jsx } from "react/jsx-runtime";
import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import MockCurrentLayoutProvider from "@foxglove/studio-base/providers/CurrentLayoutProvider/MockCurrentLayoutProvider";
import PanelSetup from "@foxglove/studio-base/stories/PanelSetup";
import PanelSettings from ".";
export default {
    title: "components/PanelSettings",
    component: PanelSettings,
    decorators: [
        (Story) => (_jsx("div", { style: { margin: 30, height: 400 }, children: _jsx(DndProvider, { backend: HTML5Backend, children: _jsx(MockCurrentLayoutProvider, { children: _jsx(Story, {}) }) }) })),
    ],
};
const panels = [
    { title: "Sample", type: "Sample1", module: async () => await new Promise(() => { }) },
];
class MockPanelCatalog {
    getPanels() {
        return panels;
    }
    getPanelByType(type) {
        return panels.find((panel) => !panel.config && panel.type === type);
    }
}
const fixture = { topics: [], datatypes: new Map(), frame: {}, layout: "Sample1!abc" };
const selectedPanelIds = ["Sample1!abc"];
export const NoPanelSelected = {
    render: () => {
        return (_jsx(PanelSetup, { panelCatalog: new MockPanelCatalog(), fixture: fixture, omitDragAndDrop: true, children: _jsx(PanelSettings, {}) }));
    },
};
export const PanelSelected = {
    render: () => {
        return (_jsx(PanelSetup, { panelCatalog: new MockPanelCatalog(), fixture: { ...fixture, savedProps: { "Sample1!abc": { someKey: "someVal" } } }, omitDragAndDrop: true, children: _jsx(PanelSettings, { selectedPanelIdsForTests: selectedPanelIds }) }));
    },
};
export const PanelSelectedWithAppBar = {
    render: () => {
        const panelId = "Sample1!abc";
        const nodes = {
            general: {
                fields: {
                    numberWithPlaceholder: {
                        input: "number",
                        label: "Number with placeholder",
                        step: 10,
                        placeholder: "3",
                    },
                },
            },
        };
        return (_jsx(PanelSetup, { panelCatalog: new MockPanelCatalog(), fixture: {
                ...fixture,
                savedProps: { [panelId]: { someKey: "someVal" } },
                panelState: {
                    settingsTrees: {
                        [panelId]: {
                            actionHandler: () => { },
                            nodes,
                        },
                    },
                },
            }, omitDragAndDrop: true, children: _jsx(PanelSettings, { selectedPanelIdsForTests: selectedPanelIds }) }));
    },
};
export const PanelLoading = {
    render: () => {
        return (_jsx(PanelSetup, { panelCatalog: new MockPanelCatalog(), fixture: fixture, omitDragAndDrop: true, children: _jsx(PanelSettings, { selectedPanelIdsForTests: selectedPanelIds }) }));
    },
};
