import { jsx as _jsx } from "react/jsx-runtime";
import PanelSetup from "@foxglove/studio-base/stories/PanelSetup";
import Indicator from "./index";
export default {
    title: "panels/IndicatorLight",
    component: Indicator,
    decorators: [
        (StoryComponent, { parameters }) => {
            return (_jsx(PanelSetup, { fixture: parameters.panelSetup?.fixture, children: _jsx(StoryComponent, {}) }));
        },
    ],
};
function makeFixture(value) {
    return {
        topics: [{ name: "/data", datatype: "foo_msgs/Bar" }],
        frame: {
            "/data": [
                {
                    topic: "/data",
                    receiveTime: { sec: 123, nsec: 456 },
                    message: { value },
                },
            ],
        },
    };
}
export const EmptyState = {
    render: () => {
        return _jsx(Indicator, {});
    },
};
export const MissingValue = {
    render: () => {
        return (_jsx(Indicator, { overrideConfig: {
                path: "/data.value",
                style: "bulb",
                rules: [
                    { operator: "=", rawValue: "true", color: "#00dd00", label: "True" },
                    { operator: "=", rawValue: "true", color: "#dd00dd", label: "False" },
                ],
                fallbackColor: "#dddd00",
                fallbackLabel: "Fallback",
            } }));
    },
};
export const BackgroundStyle = {
    render: () => {
        return (_jsx(Indicator, { overrideConfig: {
                path: "/data.value",
                style: "background",
                rules: [
                    { operator: "=", rawValue: "true", color: "#00dd00", label: "True" },
                    { operator: "=", rawValue: "true", color: "#dd00dd", label: "False" },
                ],
                fallbackColor: "#dddd00",
                fallbackLabel: "Fallback",
            } }));
    },
};
const BooleanStory = () => {
    return (_jsx(Indicator, { overrideConfig: {
            path: "/data.value",
            style: "bulb",
            rules: [
                { operator: "=", rawValue: "true", color: "#00dd00", label: "True" },
                { operator: "=", rawValue: "false", color: "#dd00dd", label: "False" },
            ],
            fallbackColor: "#dddd00",
            fallbackLabel: "Fallback",
        } }));
};
export const BooleanTrue = {
    render: () => _jsx(BooleanStory, {}),
    parameters: { panelSetup: { fixture: makeFixture(true) } },
};
export const BooleanFalse = {
    render: () => _jsx(BooleanStory, {}),
    parameters: { panelSetup: { fixture: makeFixture(false) } },
};
export const String = {
    render: function Story() {
        return (_jsx(Indicator, { overrideConfig: {
                path: "/data.value",
                style: "bulb",
                rules: [{ operator: "=", rawValue: "hello", color: "#00dd00", label: "Hello" }],
                fallbackColor: "#dddd00",
                fallbackLabel: "Fallback",
            } }));
    },
    parameters: { panelSetup: { fixture: makeFixture("hello") } },
};
const NumberStory = () => {
    return (_jsx(Indicator, { overrideConfig: {
            path: "/data.value",
            style: "bulb",
            rules: [
                { operator: "<", rawValue: "0", color: "#00dd00", label: "Negative" },
                { operator: "=", rawValue: "0", color: "#929292", label: "Zero" },
                { operator: ">", rawValue: "0", color: "#dd00dd", label: "Positive" },
            ],
            fallbackColor: "#dddd00",
            fallbackLabel: "Fallback",
        } }));
};
export const NumberNegative = {
    render: () => _jsx(NumberStory, {}),
    parameters: { panelSetup: { fixture: makeFixture(-1) } },
};
export const NumberZero = {
    render: () => _jsx(NumberStory, {}),
    parameters: { panelSetup: { fixture: makeFixture(0) } },
};
export const NumberPositive = {
    render: () => _jsx(NumberStory, {}),
    parameters: { panelSetup: { fixture: makeFixture(1) } },
};
export const MessagePathWithFilter = {
    render: function Story() {
        return (_jsx(Indicator, { overrideConfig: {
                path: `/data{id=="b"}.value`,
                style: "bulb",
                rules: [
                    { operator: "=", rawValue: "true", color: "#00dd00", label: "True" },
                    { operator: "=", rawValue: "false", color: "#dd00dd", label: "False" },
                ],
                fallbackColor: "#dddd00",
                fallbackLabel: "Fallback",
            } }));
    },
    parameters: {
        panelSetup: {
            fixture: {
                topics: [{ name: "/data", datatype: "foo_msgs/Bar" }],
                frame: {
                    "/data": [
                        {
                            topic: "/data",
                            receiveTime: { sec: 123, nsec: 456 },
                            message: { id: "a", value: false },
                        },
                        {
                            topic: "/data",
                            receiveTime: { sec: 123, nsec: 456 },
                            message: { id: "b", value: true },
                        },
                        {
                            topic: "/data",
                            receiveTime: { sec: 123, nsec: 456 },
                            message: { id: "c", value: false },
                        },
                    ],
                },
            },
        },
    },
};
