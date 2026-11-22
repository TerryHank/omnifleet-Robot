import { jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { useTheme } from "@mui/material";
import { userEvent } from "@storybook/testing-library";
import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import Panel from "@foxglove/studio-base/components/Panel";
import { PanelCatalog as PanelCatalogComponent } from "@foxglove/studio-base/components/PanelCatalog";
import PanelCatalogContext from "@foxglove/studio-base/context/PanelCatalogContext";
import MockCurrentLayoutProvider from "@foxglove/studio-base/providers/CurrentLayoutProvider/MockCurrentLayoutProvider";
const SamplePanel1 = () => _jsx("div", {});
SamplePanel1.panelType = "sample";
SamplePanel1.defaultConfig = {};
const SamplePanel2 = () => _jsx("div", {});
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
    title: "components/PanelList",
    component: ({ mode }) => _jsx(PanelCatalogComponent, { mode: mode, onPanelSelect: () => { } }),
    parameters: { colorScheme: "dark" },
    decorators: [
        (Wrapped) => {
            const theme = useTheme();
            return (_jsx(DndProvider, { backend: HTML5Backend, children: _jsx(PanelCatalogContext.Provider, { value: new MockPanelCatalog(), children: _jsx(MockCurrentLayoutProvider, { children: _jsx("div", { style: { margin: 50, height: 480, backgroundColor: theme.palette.background.paper }, children: _jsx(Wrapped, {}) }) }) }) }));
        },
    ],
    play: async ({ args }) => {
        const { keyboard } = userEvent.setup();
        if (args.inputValue) {
            await keyboard(args.inputValue);
        }
        args.events?.map(async (keypress) => {
            await keyboard(keypress);
        });
    },
};
export const List = {
    name: "Panel list",
};
export const PanelGrid = {
    args: { mode: "grid" },
};
export const FilteredPanelList = {
    args: { inputValue: "AAA" },
};
export const FilteredPanelGrid = {
    args: { mode: "grid", inputValue: "AAA" },
};
export const FilteredPanelGridWithDescription = {
    args: { mode: "grid", inputValue: "description" },
};
export const FilteredPanelListLight = {
    args: { inputValue: "AAA" },
    parameters: { colorScheme: "light" },
};
export const NavigatingArrows = {
    args: { events: ["[ArrowDown]", "[ArrowDown]", "[ArrowUp]"] },
    name: "Navigating panel list with arrow keys",
};
export const NavigatingArrowsWrap = {
    args: { events: ["[ArrowUp]"] },
    name: "Navigating up from top of panel list will scroll to highlighted last item",
};
export const NoResultsFirst = {
    args: { inputValue: "regular" },
    name: "Filtered panel list without results in 1st category",
};
export const NoResultsLast = {
    args: { inputValue: "preconfigured" },
    name: "Filtered panel list without results in last category",
};
export const NoResultsAnyList = {
    args: { inputValue: "WWW" },
    name: "Filtered panel list without results in any category",
};
export const NoResultsAnyGrid = {
    args: { mode: "grid", inputValue: "WWW" },
    name: "Filtered panel grid without results in any category",
};
export const CaseInsensitiveFilter = {
    args: { inputValue: "pA" },
    name: "Case-insensitive filtering and highlight submenu",
};
export const PanelListChinese = {
    parameters: { forceLanguage: "zh" },
};
export const PanelListJapanese = {
    parameters: { forceLanguage: "ja" },
};
export const NoResultsChinese = {
    ...NoResultsAnyGrid,
    parameters: { forceLanguage: "zh" },
};
export const NoResultsJapanese = {
    ...NoResultsAnyGrid,
    parameters: { forceLanguage: "ja" },
};
