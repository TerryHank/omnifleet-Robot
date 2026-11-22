import { jsx as _jsx, Fragment as _Fragment, jsxs as _jsxs } from "react/jsx-runtime";
import { fireEvent, screen, waitFor } from "@storybook/testing-library";
import { useEffect, useState } from "react";
import MultiProvider from "@foxglove/studio-base/components/MultiProvider";
import Panel from "@foxglove/studio-base/components/Panel";
import { usePanelContext } from "@foxglove/studio-base/components/PanelContext";
import PanelToolbar from "@foxglove/studio-base/components/PanelToolbar";
import PanelCatalogContext from "@foxglove/studio-base/context/PanelCatalogContext";
import Tab from "@foxglove/studio-base/panels/Tab";
import MockCurrentLayoutProvider from "@foxglove/studio-base/providers/CurrentLayoutProvider/MockCurrentLayoutProvider";
import EventsProvider from "@foxglove/studio-base/providers/EventsProvider";
import PanelSetup from "@foxglove/studio-base/stories/PanelSetup";
import Workspace from "./Workspace";
export default {
    title: "Workspace",
    component: Workspace,
    parameters: {
        colorScheme: "light",
    },
};
class MockPanelCatalog {
    static #fakePanel = {
        title: "Fake Panel",
        type: "Fake",
        module: async () => {
            return {
                default: Panel(Object.assign(() => (_jsxs(_Fragment, { children: [_jsx(PanelToolbar, {}), _jsx("div", { children: "I\u2019m a fake panel" })] })), { panelType: "Fake", defaultConfig: {} })),
            };
        },
    };
    static #droppablePanel = {
        title: "Droppable Panel",
        type: "Droppable",
        module: async () => {
            return {
                default: Panel(Object.assign(function DroppablePanel() {
                    const { setMessagePathDropConfig } = usePanelContext();
                    const [droppedPaths, setDroppedPaths] = useState();
                    useEffect(() => {
                        setMessagePathDropConfig({
                            getDropStatus(_paths) {
                                return { canDrop: true, message: "Example drop message" };
                            },
                            handleDrop(paths) {
                                setDroppedPaths(paths);
                            },
                        });
                    }, [setMessagePathDropConfig]);
                    return (_jsxs(_Fragment, { children: [_jsx(PanelToolbar, {}), _jsx("div", { children: "Drop here!" }), droppedPaths && _jsx("pre", { children: JSON.stringify(droppedPaths, undefined, 2) })] }));
                }, { panelType: "Droppable", defaultConfig: {} })),
            };
        },
    };
    getPanels() {
        return [
            MockPanelCatalog.#fakePanel,
            MockPanelCatalog.#droppablePanel,
            { title: "Tab", type: "Tab", module: async () => ({ default: Tab }) },
        ];
    }
    getPanelByType(type) {
        return this.getPanels().find((panel) => panel.type === type);
    }
}
export const Basic = {
    args: {
        initialLayoutState: { layout: "Fake" },
    },
    render: (args) => {
        const fixture = {
            topics: [{ name: "foo topic", schemaName: "test.Foo" }],
            datatypes: new Map([
                [
                    "test.Foo",
                    {
                        definitions: [
                            { name: "bar field", type: "string" },
                            { name: "baz field", type: "string" },
                        ],
                    },
                ],
            ]),
        };
        const providers = [
            /* eslint-disable react/jsx-key */
            _jsx(PanelSetup, { fixture: fixture, children: undefined }),
            _jsx(EventsProvider, {}),
            _jsx(PanelCatalogContext.Provider, { value: new MockPanelCatalog() }),
            _jsx(MockCurrentLayoutProvider, { initialState: args.initialLayoutState }),
            /* eslint-enable react/jsx-key */
        ];
        return (_jsx(MultiProvider, { providers: providers, children: _jsx(Workspace, { disablePersistenceForStorybook: true }) }));
    },
};
export const Chinese = {
    ...Basic,
    parameters: { forceLanguage: "zh" },
};
export const Japanese = {
    ...Basic,
    parameters: { forceLanguage: "ja" },
};
export const FullscreenPanel = {
    ...Basic,
    play: async () => {
        fireEvent.click(await screen.findByTestId("panel-menu"));
        fireEvent.click(await screen.findByTestId("panel-menu-fullscreen"));
    },
};
export const DragTopicStart = {
    ...Basic,
    args: {
        initialLayoutState: {
            layout: {
                direction: "column",
                first: "Fake",
                second: "Tab!a",
            },
            configById: {
                "Tab!a": {
                    activeTabIdx: 0,
                    tabs: [
                        { title: "Tab A", layout: { direction: "row", first: "Fake", second: "Droppable" } },
                    ],
                },
            },
        },
    },
    play: async () => {
        fireEvent.click(await screen.findByText("Topics"));
        const handle = await screen.findByTestId("TopicListDragHandle");
        fireEvent.dragStart(handle);
    },
};
export const DragTopicOver = {
    ...DragTopicStart,
    play: async () => {
        fireEvent.click(await screen.findByText("Topics"));
        const handle = await screen.findByTestId("TopicListDragHandle");
        fireEvent.dragStart(handle);
        const dest = await screen.findByText("Drop here!");
        fireEvent.dragOver(dest);
    },
};
export const DragTopicDrop = {
    ...DragTopicStart,
    play: async () => {
        fireEvent.click(await screen.findByText("Topics"));
        const handle = await screen.findByTestId("TopicListDragHandle");
        fireEvent.dragStart(handle);
        const dest = await screen.findByText("Drop here!");
        fireEvent.dragOver(dest);
        fireEvent.drop(dest);
    },
};
export const DragPathDrop = {
    ...DragTopicStart,
    play: async () => {
        fireEvent.click(await screen.findByText("Topics"));
        fireEvent.change(await screen.findByPlaceholderText("Filter by topic or schema name…"), {
            target: { value: "foobar" },
        });
        const handle = await waitFor(async () => {
            const handles = await screen.findAllByTestId("TopicListDragHandle");
            if (handles.length < 2) {
                throw new Error("Expected 2 drag handles");
            }
            return handles[1];
        });
        fireEvent.dragStart(handle);
        const dest = await screen.findByText("Drop here!");
        fireEvent.dragOver(dest);
        fireEvent.drop(dest);
    },
};
export const DragMultipleItems = {
    ...DragTopicStart,
    play: async () => {
        fireEvent.click(await screen.findByText("Topics"));
        fireEvent.change(await screen.findByPlaceholderText("Filter by topic or schema name…"), {
            target: { value: "fooba" },
        });
        fireEvent.click(await screen.findByText((_content, element) => element instanceof HTMLSpanElement && element.textContent === '."bar field"'));
        fireEvent.click(await screen.findByText((_content, element) => element instanceof HTMLSpanElement && element.textContent === '."baz field"'), { metaKey: true });
        const handle = await waitFor(async () => {
            const handles = await screen.findAllByTestId("TopicListDragHandle");
            if (handles.length < 3) {
                throw new Error("Expected 3 drag handles");
            }
            return handles[2];
        });
        fireEvent.dragStart(handle);
        const dest = await screen.findByText("Drop here!");
        fireEvent.dragOver(dest);
        fireEvent.drop(dest);
    },
};
