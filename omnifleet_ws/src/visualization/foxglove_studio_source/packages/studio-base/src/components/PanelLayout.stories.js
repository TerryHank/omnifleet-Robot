import { jsx as _jsx, Fragment as _Fragment, jsxs as _jsxs } from "react/jsx-runtime";
import { fireEvent, screen } from "@storybook/testing-library";
import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import Panel from "@foxglove/studio-base/components/Panel";
import PanelToolbar from "@foxglove/studio-base/components/PanelToolbar";
import PanelSetup from "@foxglove/studio-base/stories/PanelSetup";
import PanelLayout from "./PanelLayout";
async function openPanelMenu() {
    const buttons = await screen.findAllByTestId("panel-menu");
    fireEvent.click(buttons[0]);
}
async function goFullScreen() {
    await openPanelMenu();
    fireEvent.click(screen.getAllByTestId("panel-menu-fullscreen")[0]);
}
const allPanels = [
    { title: "Some Panel", type: "Sample1", module: async () => await new Promise(() => { }) },
    {
        title: "Broken Panel",
        type: "Sample2",
        module: async () => {
            return {
                default: Panel(Object.assign(function BrokenPanel() {
                    throw new Error("I don't work!");
                }, { panelType: "Sample2", defaultConfig: {} })),
            };
        },
    },
    {
        title: "Okay Panel",
        type: "Sample3",
        module: async () => {
            return {
                default: Panel(Object.assign(function OkayPanel({ config: { x } }) {
                    return (_jsxs(_Fragment, { children: [_jsx(PanelToolbar, {}), "Hi ", x] }));
                }, { panelType: "Sample3", defaultConfig: { x: 0 } })),
            };
        },
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
    title: "components/PanelLayout",
};
export const PanelNotFound = {
    render: function Story() {
        return (_jsx(DndProvider, { backend: HTML5Backend, children: _jsx(PanelSetup, { fixture: { topics: [], datatypes: new Map(), frame: {}, layout: "UnknownPanel!4co6n9d" }, omitDragAndDrop: true, children: _jsx(PanelLayout, {}) }) }));
    },
    parameters: { colorScheme: "dark" },
    play: openPanelMenu,
};
export const PanelNotFoundLight = {
    ...PanelNotFound,
    parameters: { colorScheme: "light" },
    play: openPanelMenu,
};
export const PanelWithError = {
    render: () => {
        return (_jsx(DndProvider, { backend: HTML5Backend, children: _jsx(PanelSetup, { panelCatalog: new MockPanelCatalog(), fixture: { topics: [], datatypes: new Map(), frame: {}, layout: "Sample2!4co6n9d" }, omitDragAndDrop: true, children: _jsx(PanelLayout, {}) }) }));
    },
};
export const RemoveUnknownPanel = {
    render: function Story() {
        return (_jsx(DndProvider, { backend: HTML5Backend, children: _jsx(PanelSetup, { fixture: { topics: [], datatypes: new Map(), frame: {}, layout: "UnknownPanel!4co6n9d" }, omitDragAndDrop: true, children: _jsx(PanelLayout, {}) }) }));
    },
    play: async () => {
        (await screen.findAllByTestId("panel-menu")).forEach((button) => fireEvent.click(button));
        (await screen.findAllByTestId("panel-menu-remove")).forEach((button) => fireEvent.click(button));
    },
};
export const EmptyLayout = {
    render: () => {
        return (_jsx(PanelSetup, { fixture: { layout: undefined }, children: _jsx(PanelLayout, {}) }));
    },
};
export const EmptyLayoutChinese = {
    ...EmptyLayout,
    parameters: { forceLanguage: "zh" },
};
export const EmptyLayoutJapanese = {
    ...EmptyLayout,
    parameters: { forceLanguage: "ja" },
};
export const PanelLoading = {
    render: () => {
        return (_jsx(DndProvider, { backend: HTML5Backend, children: _jsx(PanelSetup, { panelCatalog: new MockPanelCatalog(), fixture: { topics: [], datatypes: new Map(), frame: {}, layout: "Sample1!4co6n9d" }, omitDragAndDrop: true, children: _jsx(PanelLayout, {}) }) }));
    },
};
export const FullScreen = {
    render: function Story() {
        return (_jsx(DndProvider, { backend: HTML5Backend, children: _jsx(PanelSetup, { panelCatalog: new MockPanelCatalog(), fixture: {
                    topics: [],
                    datatypes: new Map(),
                    frame: {},
                    layout: { first: "Sample3!a", second: "Sample3!b", direction: "row" },
                    savedProps: {
                        "Sample3!a": { x: 1 },
                        "Sample3!b": { x: 2 },
                    },
                }, omitDragAndDrop: true, children: _jsx(PanelLayout, {}) }) }));
    },
    parameters: { colorScheme: "dark" },
    play: goFullScreen,
};
export const FullScreenLight = {
    ...FullScreen,
    parameters: { colorScheme: "light" },
    play: goFullScreen,
};
