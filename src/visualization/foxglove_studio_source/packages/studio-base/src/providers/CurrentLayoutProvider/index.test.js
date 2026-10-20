import { Fragment as _Fragment, jsx as _jsx } from "react/jsx-runtime";
/** @jest-environment jsdom */
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { render, act, renderHook } from "@testing-library/react";
import { SnackbarProvider } from "notistack";
import { useEffect } from "react";
import { useCurrentLayoutActions, useCurrentLayoutSelector, } from "@foxglove/studio-base/context/CurrentLayoutContext";
import CurrentLayoutProvider, { MAX_SUPPORTED_LAYOUT_VERSION, } from "@foxglove/studio-base/providers/CurrentLayoutProvider";
describe("CurrentLayoutProvider", () => {
    it("refuses to load an incompatible layout", async () => {
        const all = new Array();
        function SetUnsupportedLayout() {
            const layoutState = useCurrentLayoutSelector((state) => state);
            const actions = useCurrentLayoutActions();
            useEffect(() => {
                all.push(layoutState);
            }, [layoutState]);
            useEffect(() => {
                actions.setCurrentLayout({
                    data: {
                        configById: { "Foo!bar": { setting: 1 } },
                        globalVariables: { var: "hello" },
                        layout: "Foo!bar",
                        playbackConfig: { speed: 0.1 },
                        userNodes: { node1: { name: "node", sourceCode: "node()" } },
                        version: MAX_SUPPORTED_LAYOUT_VERSION + 1,
                    },
                });
            }, [actions]);
            return _jsx(_Fragment, {});
        }
        const { getByText } = render(_jsx(SetUnsupportedLayout, {}), {
            wrapper: (props) => {
                return (_jsx(SnackbarProvider, { children: _jsx(CurrentLayoutProvider, { children: props.children }) }));
            },
        });
        expect(getByText("Incompatible layout version")).toBeDefined();
        expect(all.length).toBe(1);
        expect(all).toEqual([{ selectedLayout: undefined }]);
        console.warn.mockClear();
    });
    it("keeps identity of action functions when modifying layout", async () => {
        const all = [];
        const { result } = renderHook(() => {
            const actions = useCurrentLayoutActions();
            all.push(actions);
            return actions;
        }, {
            wrapper: function Wrapper({ children }) {
                return (_jsx(SnackbarProvider, { children: _jsx(CurrentLayoutProvider, { children: children }) }));
            },
        });
        const actions = result.current;
        expect(result.current).toBe(actions);
        act(() => {
            result.current.savePanelConfigs({
                configs: [{ id: "ExamplePanel!1", config: { foo: "bar" } }],
            });
        });
        expect(result.current.savePanelConfigs).toBe(actions.savePanelConfigs);
        console.warn.mockClear();
    });
});
