import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useLayoutEffect, useState } from "react";
import ReactDOM from "react-dom";
import { toSec } from "@foxglove/rostime";
import ErrorBoundary from "@foxglove/studio-base/components/ErrorBoundary";
import MockPanelContextProvider from "@foxglove/studio-base/components/MockPanelContextProvider";
import PanelSetup from "@foxglove/studio-base/stories/PanelSetup";
import PanelExtensionAdapter, { VERSION_CONFIG_KEY } from "./PanelExtensionAdapter";
export default {
    title: "PanelExtensionAdapter",
    component: PanelExtensionAdapter,
};
export const CatchRenderError = {
    render: () => {
        const initPanel = (context) => {
            context.watch("topics");
            context.onRender = () => {
                const err = new Error("sample render error");
                // The default stacktrace contains paths from the webpack bundle. These paths have the bundle
                // identifier/hash and change whenever the bundle changes. This makes the story change.
                // To avoid the story changing we set the stacktrace explicitly.
                err.stack = "sample stacktrace";
                throw err;
            };
        };
        return (_jsx(PanelSetup, { fixture: {
                topics: [
                    {
                        name: "/topic",
                        schemaName: "test_msgs/Sample",
                    },
                ],
                datatypes: new Map(),
                frame: {},
                layout: "UnknownPanel!4co6n9d",
            }, children: _jsx(MockPanelContextProvider, { children: _jsx(ErrorBoundary, { children: _jsx(PanelExtensionAdapter, { config: {}, saveConfig: () => { }, initPanel: initPanel }) }) }) }));
    },
};
function SimplePanel({ context }) {
    const [currentTime, setCurrentTime] = useState(undefined);
    const [parameters, setParameters] = useState(new Map());
    useLayoutEffect(() => {
        context.watch("currentTime");
        context.watch("parameters");
        context.onRender = (renderState, done) => {
            setCurrentTime(renderState.currentTime);
            if (renderState.parameters != undefined) {
                setParameters(renderState.parameters);
            }
            done();
        };
    }, [context]);
    return (_jsxs("div", { children: [_jsx("h2", { children: "Simple Panel" }), _jsx("h3", { children: "Current Time" }), _jsx("div", { children: currentTime ? toSec(currentTime) : "-" }), _jsx("h3", { children: "Parameters" }), _jsx("div", { children: JSON.stringify(Array.from(parameters)) })] }));
}
export const SimplePanelRender = {
    render: () => {
        function initPanel(context) {
            // eslint-disable-next-line react/no-deprecated
            ReactDOM.render(_jsx(SimplePanel, { context: context }), context.panelElement);
        }
        return (_jsx(PanelSetup, { fixture: {
                datatypes: new Map(),
                frame: {},
                activeData: {
                    currentTime: { sec: 1, nsec: 2 },
                    parameters: new Map([
                        ["param1", "value1"],
                        ["param2", "value2"],
                    ]),
                },
                layout: "UnknownPanel!4co6n9d",
            }, children: _jsx(MockPanelContextProvider, { children: _jsx(PanelExtensionAdapter, { config: {}, saveConfig: () => { }, initPanel: initPanel }) }) }));
    },
};
export const ConfigTooNew = {
    render: () => {
        function initPanel() {
            throw new Error("Should not be called");
        }
        return (_jsx(PanelSetup, { children: _jsx(MockPanelContextProvider, { children: _jsx(PanelExtensionAdapter, { highestSupportedConfigVersion: 1, config: { [VERSION_CONFIG_KEY]: 2 }, saveConfig: () => { }, initPanel: initPanel }) }) }));
    },
};
