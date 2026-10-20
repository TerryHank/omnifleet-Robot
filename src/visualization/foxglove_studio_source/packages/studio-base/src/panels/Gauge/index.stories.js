import { jsx as _jsx } from "react/jsx-runtime";
import PanelSetup from "@foxglove/studio-base/stories/PanelSetup";
import GaugePanel from "./index";
export default {
    title: "panels/Gauge",
    component: GaugePanel,
    decorators: [
        (StoryComponent, { parameters }) => {
            return (_jsx(PanelSetup, { fixture: parameters.panelSetup?.fixture, children: _jsx(StoryComponent, {}) }));
        },
    ],
};
function makeFixture(value) {
    return {
        topics: [{ name: "/data", datatype: "foo_msgs/Bar" }],
        datatypes: new Map([
            ["foo_msgs/Bar", { name: "Bar", definitions: [{ name: "value", type: "float32" }] }],
        ]),
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
        return _jsx(GaugePanel, {});
    },
};
export const InvalidValue = {
    render: function Story() {
        return _jsx(GaugePanel, { overrideConfig: { path: "/data.value", minValue: 0, maxValue: 1 } });
    },
    parameters: { panelSetup: { fixture: makeFixture(NaN) } },
};
export const Rainbow = {
    render: function Story() {
        return (_jsx(GaugePanel, { overrideConfig: {
                path: "/data.value",
                minValue: 0,
                maxValue: 1,
                colorMode: "colormap",
                colorMap: "rainbow",
            } }));
    },
    parameters: { panelSetup: { fixture: makeFixture(0.3) } },
};
export const Turbo = {
    render: function Story() {
        return (_jsx(GaugePanel, { overrideConfig: {
                path: "/data.value",
                minValue: 0,
                maxValue: 1,
                colorMode: "colormap",
                colorMap: "turbo",
            } }));
    },
    parameters: { panelSetup: { fixture: makeFixture(0.3) } },
};
export const TurboReverse = {
    render: function Story() {
        return (_jsx(GaugePanel, { overrideConfig: {
                path: "/data.value",
                minValue: 0,
                maxValue: 1,
                colorMode: "colormap",
                colorMap: "turbo",
                reverse: true,
            } }));
    },
    parameters: { panelSetup: { fixture: makeFixture(0.3) } },
};
export const CustomGradient = {
    render: function Story() {
        return (_jsx(GaugePanel, { overrideConfig: {
                path: "/data.value",
                minValue: 0,
                maxValue: 1,
                colorMode: "gradient",
                gradient: ["#ec9a57", "#65c6ff"],
            } }));
    },
    parameters: { panelSetup: { fixture: makeFixture(0.3) } },
};
export const CustomGradientReverse = {
    render: function Story() {
        return (_jsx(GaugePanel, { overrideConfig: {
                path: "/data.value",
                minValue: 0,
                maxValue: 1,
                colorMode: "gradient",
                gradient: ["#ec9a57", "#65c6ff"],
                reverse: true,
            } }));
    },
    parameters: { panelSetup: { fixture: makeFixture(0.3) } },
};
export const MinValue = {
    render: function Story() {
        return _jsx(GaugePanel, { overrideConfig: { path: "/data.value", minValue: 0, maxValue: 1 } });
    },
    parameters: { panelSetup: { fixture: makeFixture(0) } },
};
export const MaxValue = {
    render: function Story() {
        return _jsx(GaugePanel, { overrideConfig: { path: "/data.value", minValue: 0, maxValue: 1 } });
    },
    parameters: { panelSetup: { fixture: makeFixture(1) } },
};
export const TooLow = {
    render: function Story() {
        return _jsx(GaugePanel, { overrideConfig: { path: "/data.value", minValue: 0, maxValue: 1 } });
    },
    parameters: { panelSetup: { fixture: makeFixture(-1) } },
};
export const TooHigh = {
    render: function Story() {
        return _jsx(GaugePanel, { overrideConfig: { path: "/data.value", minValue: 0, maxValue: 1 } });
    },
    parameters: { panelSetup: { fixture: makeFixture(2) } },
};
export const CustomRange = {
    render: function Story() {
        return _jsx(GaugePanel, { overrideConfig: { path: "/data.value", minValue: 5, maxValue: 7 } });
    },
    parameters: { panelSetup: { fixture: makeFixture(6.5) } },
};
export const MessagePathWithFilter = {
    render: function Story() {
        return (_jsx(GaugePanel, { overrideConfig: { path: `/data{id=="b"}.value`, minValue: 0, maxValue: 4 } }));
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
                            message: { id: "a", value: 1 },
                        },
                        {
                            topic: "/data",
                            receiveTime: { sec: 123, nsec: 456 },
                            message: { id: "b", value: 2 },
                        },
                        {
                            topic: "/data",
                            receiveTime: { sec: 123, nsec: 456 },
                            message: { id: "c", value: 3 },
                        },
                    ],
                },
            },
        },
    },
};
export const StringValue = {
    render: function Story() {
        return _jsx(GaugePanel, { overrideConfig: { path: `/data.value`, minValue: 0, maxValue: 1 } });
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
                            message: { value: "0.2" },
                        },
                    ],
                },
            },
        },
    },
};
