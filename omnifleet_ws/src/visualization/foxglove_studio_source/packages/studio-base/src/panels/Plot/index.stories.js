import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { screen, userEvent } from "@storybook/testing-library";
import { produce } from "immer";
import { useEffect, useState } from "react";
import { makeStyles } from "tss-react/mui";
import PanelSetup, { triggerWheel } from "@foxglove/studio-base/stories/PanelSetup";
import delay from "@foxglove/studio-base/util/delay";
import Plot from "./index";
import { fixture } from "./storyFixtures";
const withEndTime = (testFixture, endTime) => ({
    ...testFixture,
    activeData: { ...testFixture.activeData, endTime },
});
const paths = [
    { value: "/some_topic/location.pose.velocity", enabled: true, timestampMethod: "receiveTime" },
    {
        value: "/some_topic/location.pose.acceleration",
        enabled: true,
        timestampMethod: "receiveTime",
    },
    {
        value: "/some_topic/location.pose.acceleration.@derivative",
        enabled: true,
        timestampMethod: "receiveTime",
    },
    { value: "/boolean_topic.data", enabled: true, timestampMethod: "receiveTime" },
    { value: "/some_topic/state.items[0].speed", enabled: true, timestampMethod: "receiveTime" },
    { value: "/some_topic/location.header.stamp", enabled: true, timestampMethod: "receiveTime" },
];
const exampleConfig = {
    paths,
    xAxisVal: "timestamp",
    showLegend: true,
    isSynced: true,
    legendDisplay: "floating",
    showXAxisLabels: true,
    showYAxisLabels: true,
    showPlotValuesInLegend: false,
    sidebarDimension: 0,
};
function PlotWrapper(props) {
    const [actualFixture, setFixture] = useState();
    useEffect(() => {
        setTimeout(() => {
            setFixture(props.fixture ?? fixture);
        }, 0);
    }, [props.fixture]);
    return (_jsx(PanelSetup, { fixture: actualFixture, includeSettings: props.includeSettings, style: { ...props.style }, children: _jsx(Plot, { overrideConfig: props.config }) }));
}
export default {
    title: "panels/Plot",
    component: PlotWrapper,
    parameters: {
        colorScheme: "light",
        chromatic: { delay: 100 },
    },
};
export const Empty = {
    args: {
        includeSettings: true,
        config: Plot.defaultConfig,
    },
    parameters: { colorScheme: "light" },
};
export const LineGraph = {
    args: {
        config: exampleConfig,
    },
    name: "line graph",
    parameters: {
        colorScheme: "light",
    },
};
export const LineGraphWithValuesAndDisabledSeries = {
    args: {
        config: produce(exampleConfig, (draft) => {
            draft.paths[1].enabled = false;
            draft.showPlotValuesInLegend = true;
        }),
    },
    name: "line graph with values and disabled series",
    parameters: {
        colorScheme: "light",
    },
};
export const LineGraphWithXMinMax = {
    render: function Story() {
        return _jsx(PlotWrapper, { config: { ...exampleConfig, minXValue: 1, maxXValue: 2 } });
    },
    name: "line graph with x min & max",
    parameters: {
        colorScheme: "light",
    },
};
export const LineGraphWithXRange = {
    render: function Story() {
        return _jsx(PlotWrapper, { config: { ...exampleConfig, followingViewWidth: 3 }, includeSettings: true });
    },
    parameters: {
        colorScheme: "light",
    },
    name: "line graph with x range",
};
export const LineGraphWithSettings = {
    render: function Story() {
        return (_jsx(PlotWrapper, { config: {
                ...exampleConfig,
                minYValue: -3.1415,
                maxYValue: 0.00001,
                minXValue: 0.001234,
                maxXValue: 30,
            }, includeSettings: true }));
    },
    parameters: {
        colorScheme: "light",
    },
    name: "line graph with settings",
    play: async () => {
        const yLabel = await screen.findByTestId("settings__nodeHeaderToggle__yAxis");
        await userEvent.click(yLabel);
        const xLabel = await screen.findByTestId("settings__nodeHeaderToggle__xAxis");
        await userEvent.click(xLabel);
    },
};
export const LineGraphWithSettingsChinese = {
    ...LineGraphWithSettings,
    parameters: {
        colorScheme: "light",
        ...LineGraphWithSettings.parameters,
        forceLanguage: "zh",
    },
};
export const LineGraphWithSettingsJapanese = {
    ...LineGraphWithSettings,
    parameters: {
        colorScheme: "light",
        ...LineGraphWithSettings.parameters,
        forceLanguage: "ja",
    },
};
export const LineGraphWithLegendsHidden = {
    render: function Story() {
        return _jsx(PlotWrapper, { config: { ...exampleConfig, showLegend: false } });
    },
    name: "line graph with legends hidden",
    parameters: {
        colorScheme: "light",
    },
};
const useStyles = makeStyles()(() => ({
    PanelSetup: {
        flexDirection: "column",
        "& > *": {
            // minHeight necessary to get around otherwise flaky test because of layout
            minHeight: "50%",
        },
    },
}));
export const InALineGraphWithMultiplePlotsXAxesAreSynced = {
    render: function Story() {
        const { classes } = useStyles();
        return (_jsxs(PanelSetup, { fixture: fixture, className: classes.PanelSetup, children: [_jsx(Plot, { overrideConfig: {
                        ...exampleConfig,
                        paths: [
                            {
                                value: "/some_topic/location.pose.acceleration",
                                enabled: true,
                                timestampMethod: "receiveTime",
                            },
                        ],
                    } }), _jsx(Plot, { overrideConfig: {
                        ...exampleConfig,
                        paths: [
                            {
                                value: "/some_topic/location_subset.pose.velocity",
                                enabled: true,
                                timestampMethod: "receiveTime",
                            },
                        ],
                    } })] }));
    },
    name: "in a line graph with multiple plots, x-axes are synced",
    parameters: {
        colorScheme: "light",
    },
    play: async () => {
        await delay(100);
        const canvasEl = document.querySelector("canvas");
        // Zoom is a continuous event, so we need to simulate wheel multiple times
        if (canvasEl) {
            for (let i = 0; i < 5; i++) {
                triggerWheel(canvasEl.parentElement, 1);
            }
        }
    },
};
export const LineGraphAfterZoom = {
    render: function Story() {
        return _jsx(PlotWrapper, { config: exampleConfig });
    },
    name: "line graph after zoom",
    parameters: {
        colorScheme: "light",
    },
    play: async () => {
        await delay(100);
        const canvasEl = document.querySelector("canvas");
        // Zoom is a continuous event, so we need to simulate wheel multiple times
        if (canvasEl) {
            for (let i = 0; i < 5; i++) {
                triggerWheel(canvasEl.parentElement, 1);
            }
        }
    },
};
export const TimestampMethodHeaderStamp = {
    render: function Story() {
        return (_jsx(PlotWrapper, { config: {
                ...exampleConfig,
                paths: [
                    {
                        value: "/some_topic/location_shuffled.pose.velocity",
                        enabled: true,
                        timestampMethod: "headerStamp",
                    },
                    { value: "/boolean_topic.data", enabled: true, timestampMethod: "headerStamp" },
                ],
            } }));
    },
    name: "timestampMethod: headerStamp",
    parameters: {
        colorScheme: "light",
    },
};
export const LongPath = {
    render: function Story() {
        return (_jsx(PlotWrapper, { style: { maxWidth: 250 }, config: {
                ...exampleConfig,
                paths: [
                    {
                        value: "/some_topic/location.pose.velocity",
                        enabled: true,
                        timestampMethod: "receiveTime",
                    },
                ],
            } }));
    },
    name: "long path",
    parameters: {
        colorScheme: "light",
    },
};
export const HiddenConnectingLines = {
    render: function Story() {
        return (_jsx(PlotWrapper, { config: {
                ...exampleConfig,
                paths: [
                    {
                        value: "/some_topic/location.pose.velocity",
                        enabled: true,
                        showLine: false,
                        timestampMethod: "receiveTime",
                    },
                    {
                        value: "/some_topic/location.pose.acceleration",
                        enabled: true,
                        showLine: true,
                        timestampMethod: "receiveTime",
                    },
                ],
            } }));
    },
    name: "hidden connecting lines",
    parameters: {
        colorScheme: "light",
    },
};
export const ReferenceLine = {
    render: function Story() {
        return (_jsx(PlotWrapper, { config: {
                ...exampleConfig,
                paths: [
                    { value: "0", enabled: true, timestampMethod: "receiveTime" }, // Test typing a period for decimal values. value: "1.", enabled: true, timestampMethod: "receiveTime",
                    { value: "1.", enabled: true, timestampMethod: "receiveTime" },
                    { value: "1.5", enabled: true, timestampMethod: "receiveTime" },
                    { value: "1", enabled: false, timestampMethod: "receiveTime" },
                ],
                minYValue: "-1",
                maxYValue: "2",
            } }));
    },
    name: "reference line",
    parameters: {
        colorScheme: "light",
    },
};
export const WithMinAndMaxYValues = {
    render: function Story() {
        return (_jsx(PlotWrapper, { includeSettings: true, config: {
                ...exampleConfig,
                paths: [
                    {
                        value: "/some_topic/location.pose.velocity",
                        enabled: true,
                        timestampMethod: "receiveTime",
                    },
                ],
                minYValue: "1",
                maxYValue: "2.8",
            } }));
    },
    parameters: {
        colorScheme: "light",
    },
    name: "with min and max Y values",
    play: async () => {
        const label = await screen.findByText("Y Axis");
        await userEvent.click(label);
    },
};
export const WithJustMinYValueLessThanMinimumValue = {
    render: function Story() {
        return (_jsx(PlotWrapper, { config: {
                ...exampleConfig,
                paths: [
                    {
                        value: "/some_topic/location.pose.velocity",
                        enabled: true,
                        timestampMethod: "receiveTime",
                    },
                ],
                minYValue: "1",
            } }));
    },
    name: "with just min Y value less than minimum value",
    parameters: {
        colorScheme: "light",
    },
};
export const WithJustMinYValueMoreThanMinimumValue = {
    render: function Story() {
        return (_jsx(PlotWrapper, { config: {
                ...exampleConfig,
                paths: [
                    {
                        value: "/some_topic/location.pose.velocity",
                        enabled: true,
                        timestampMethod: "receiveTime",
                    },
                ],
                minYValue: "1.4",
            } }));
    },
    name: "with just min Y value more than minimum value",
    parameters: {
        colorScheme: "light",
    },
};
export const WithJustMinYValueMoreThanMaximumValue = {
    render: function Story() {
        return (_jsx(PlotWrapper, { config: {
                ...exampleConfig,
                paths: [
                    {
                        value: "/some_topic/location.pose.velocity",
                        enabled: true,
                        timestampMethod: "receiveTime",
                    },
                ],
                minYValue: "5",
            } }));
    },
    name: "with just min Y value more than maximum value",
    parameters: {
        colorScheme: "light",
    },
};
export const WithJustMaxYValueLessThanMaximumValue = {
    render: function Story() {
        return (_jsx(PlotWrapper, { config: {
                ...exampleConfig,
                paths: [
                    {
                        value: "/some_topic/location.pose.velocity",
                        enabled: true,
                        timestampMethod: "receiveTime",
                    },
                ],
                maxYValue: "1.8",
            } }));
    },
    name: "with just max Y value less than maximum value",
    parameters: {
        colorScheme: "light",
    },
};
export const WithJustMaxYValueMoreThanMaximumValue = {
    render: function Story() {
        return (_jsx(PlotWrapper, { config: {
                ...exampleConfig,
                paths: [
                    {
                        value: "/some_topic/location.pose.velocity",
                        enabled: true,
                        timestampMethod: "receiveTime",
                    },
                ],
                maxYValue: "2.8",
            } }));
    },
    name: "with just max Y value more than maximum value",
    parameters: {
        colorScheme: "light",
    },
};
export const WithJustMaxYValueLessThanMinimumValue = {
    render: function Story() {
        return (_jsx(PlotWrapper, { config: {
                ...exampleConfig,
                paths: [
                    {
                        value: "/some_topic/location.pose.velocity",
                        enabled: true,
                        timestampMethod: "receiveTime",
                    },
                ],
                maxYValue: "1",
            } }));
    },
    name: "with just max Y value less than minimum value",
    parameters: {
        colorScheme: "light",
    },
};
export const IndexBasedXAxisForArray = {
    render: function Story() {
        return (_jsx(PlotWrapper, { config: {
                ...exampleConfig,
                xAxisVal: "index",
                paths: [
                    {
                        value: "/some_topic/state.items[:].speed",
                        enabled: true,
                        timestampMethod: "receiveTime",
                    }, // Should show up only in the legend: For now index plots always use playback data, and ignore preloaded data.
                    { value: "/preloaded_topic.data", enabled: true, timestampMethod: "receiveTime" },
                ],
            } }));
    },
    name: "index-based x-axis for array",
    parameters: {
        colorScheme: "light",
    },
};
export const IndexBasedXAxisForArrayWithUpdate = {
    render: function Story() {
        const [ourFixture, setOurFixture] = useState(structuredClone(fixture));
        useEffect(() => {
            setOurFixture((oldValue) => {
                return {
                    ...oldValue,
                    frame: {
                        "/some_topic/state": [
                            {
                                topic: "/some_topic/state",
                                receiveTime: { sec: 3, nsec: 0 },
                                message: {
                                    header: { stamp: { sec: 3, nsec: 0 } },
                                    items: [
                                        { id: 10, speed: 1 },
                                        { id: 42, speed: 10 },
                                    ],
                                },
                                schemaName: "msgs/State",
                                sizeInBytes: 0,
                            },
                        ],
                    },
                };
            });
        }, []);
        return (_jsx(PlotWrapper, { fixture: ourFixture, config: {
                ...exampleConfig,
                xAxisVal: "index",
                paths: [
                    {
                        value: "/some_topic/state.items[:].speed",
                        enabled: true,
                        timestampMethod: "receiveTime",
                    },
                ],
            } }));
    },
    name: "index-based x-axis for array with update",
    parameters: {
        colorScheme: "light",
    },
};
export const CustomXAxisTopic = {
    render: function Story() {
        return (_jsx(PlotWrapper, { config: {
                ...exampleConfig,
                xAxisVal: "custom",
                paths: [
                    {
                        value: "/some_topic/location.pose.acceleration",
                        enabled: true,
                        timestampMethod: "receiveTime",
                    },
                ],
                xAxisPath: { value: "/some_topic/location.pose.velocity", enabled: true },
            } }));
    },
    name: "custom x-axis topic",
    parameters: {
        colorScheme: "light",
    },
};
export const CustomXAxisTopicWithXLimits = {
    render: function Story() {
        return (_jsx(PlotWrapper, { config: {
                ...exampleConfig,
                xAxisVal: "custom",
                minXValue: 1.3,
                maxXValue: 1.8,
                paths: [
                    {
                        value: "/some_topic/location.pose.acceleration",
                        enabled: true,
                        timestampMethod: "receiveTime",
                    },
                ],
                xAxisPath: { value: "/some_topic/location.pose.velocity", enabled: true },
            } }));
    },
    parameters: {
        colorScheme: "light",
    },
    name: "custom x-axis topic with x limits",
};
export const CurrentCustomXAxisTopic = {
    render: function Story() {
        // As above, but just shows a single point instead of the whole line.
        return (_jsx(PlotWrapper, { config: {
                ...exampleConfig,
                xAxisVal: "currentCustom",
                paths: [
                    {
                        value: "/some_topic/location.pose.acceleration",
                        enabled: true,
                        timestampMethod: "receiveTime",
                    },
                ],
                xAxisPath: { value: "/some_topic/location.pose.velocity", enabled: true },
            } }));
    },
    name: "current custom x-axis topic",
    parameters: {
        colorScheme: "light",
    },
};
export const CustomXAxisTopicWithMismatchedDataLengths = {
    render: function Story() {
        return (_jsx(PlotWrapper, { config: {
                ...exampleConfig,
                xAxisVal: "custom",
                paths: [
                    // Extra items in y-axis
                    {
                        value: "/some_topic/location.pose.acceleration",
                        enabled: true,
                        timestampMethod: "receiveTime",
                    }, // Same number of items
                    {
                        value: "/some_topic/location_subset.pose.acceleration",
                        enabled: true,
                        timestampMethod: "receiveTime",
                    }, // Fewer items in y-axis
                    {
                        value: "/some_topic/state.items[:].speed",
                        enabled: true,
                        timestampMethod: "receiveTime",
                    },
                ],
                xAxisPath: { value: "/some_topic/location_subset.pose.velocity", enabled: true },
            } }));
    },
    name: "custom x-axis topic with mismatched data lengths",
    parameters: {
        colorScheme: "light",
    },
};
export const SuperCloseValues = {
    render: function Story() {
        return (_jsx(PlotWrapper, { fixture: {
                datatypes: new Map(Object.entries({
                    "std_msgs/Float32": {
                        definitions: [{ name: "data", type: "float32", isArray: false }],
                    },
                })),
                topics: [{ name: "/some_number", schemaName: "std_msgs/Float32" }],
                activeData: {
                    startTime: { sec: 0, nsec: 0 },
                    endTime: { sec: 10, nsec: 0 },
                    isPlaying: false,
                    speed: 0.2,
                },
                frame: {
                    "/some_number": [
                        {
                            topic: "/some_number",
                            receiveTime: { sec: 0, nsec: 0 },
                            message: { data: 1.8548483304974972 },
                            schemaName: "std_msgs/Float32",
                            sizeInBytes: 0,
                        },
                        {
                            topic: "/some_number",
                            receiveTime: { sec: 1, nsec: 0 },
                            message: { data: 1.8548483304974974 },
                            schemaName: "std_msgs/Float32",
                            sizeInBytes: 0,
                        },
                    ],
                },
            }, config: {
                ...exampleConfig,
                paths: [{ value: "/some_number.data", enabled: true, timestampMethod: "receiveTime" }],
            } }));
    },
    name: "super close values",
    parameters: {
        colorScheme: "light",
    },
};
export const TimeValues = {
    render: function Story() {
        return (_jsx(PlotWrapper, { config: {
                ...exampleConfig,
                xAxisVal: "custom",
                paths: [
                    {
                        value: "/some_topic/location.pose.velocity",
                        enabled: true,
                        timestampMethod: "receiveTime",
                    },
                ],
                xAxisPath: { value: "/some_topic/location.header.stamp", enabled: true },
            } }));
    },
    name: "time values",
    parameters: {
        colorScheme: "light",
    },
};
export const PreloadedDataInBinaryBlocks = {
    render: function Story() {
        return (_jsx(PlotWrapper, { fixture: withEndTime(fixture, { sec: 2, nsec: 0 }), config: {
                ...exampleConfig,
                paths: [
                    { value: "/preloaded_topic.data", enabled: true, timestampMethod: "receiveTime" },
                    { value: "/preloaded_topic.data", enabled: true, timestampMethod: "headerStamp" },
                ],
            } }));
    },
    name: "preloaded data in binary blocks",
    parameters: {
        colorScheme: "light",
    },
};
export const MixedStreamedAndPreloadedData = {
    render: function Story() {
        return (_jsx(PlotWrapper, { fixture: withEndTime(fixture, { sec: 3, nsec: 0 }), config: {
                ...exampleConfig,
                paths: [
                    {
                        value: "/some_topic/state.items[0].speed",
                        enabled: true,
                        timestampMethod: "receiveTime",
                    },
                    { value: "/preloaded_topic.data", enabled: true, timestampMethod: "receiveTime" },
                ],
            } }));
    },
    name: "mixed streamed and preloaded data",
    parameters: {
        colorScheme: "light",
    },
};
export const PreloadedDataAndItsDerivative = {
    render: function Story() {
        return (_jsx(PlotWrapper, { fixture: withEndTime(fixture, { sec: 2, nsec: 0 }), config: {
                ...exampleConfig,
                paths: [
                    { value: "/preloaded_topic.data", enabled: true, timestampMethod: "receiveTime" },
                    {
                        value: "/preloaded_topic.data.@derivative",
                        enabled: true,
                        timestampMethod: "receiveTime",
                    },
                ],
            } }));
    },
    name: "preloaded data and its derivative",
    parameters: {
        colorScheme: "light",
    },
};
export const PreloadedDataAndItsNegative = {
    render: function Story() {
        return (_jsx(PlotWrapper, { fixture: withEndTime(fixture, { sec: 2, nsec: 0 }), config: {
                ...exampleConfig,
                paths: [
                    { value: "/preloaded_topic.data", enabled: true, timestampMethod: "receiveTime" },
                    {
                        value: "/preloaded_topic.data.@negative",
                        enabled: true,
                        timestampMethod: "receiveTime",
                    },
                ],
            } }));
    },
    name: "preloaded data and its negative",
    parameters: {
        colorScheme: "light",
    },
};
export const PreloadedDataAndItsAbsoluteValue = {
    render: function Story() {
        return (_jsx(PlotWrapper, { fixture: withEndTime(fixture, { sec: 2, nsec: 0 }), config: {
                ...exampleConfig,
                paths: [
                    {
                        value: "/preloaded_topic.data",
                        enabled: true,
                        timestampMethod: "receiveTime",
                        lineSize: 2,
                    },
                    {
                        value: "/preloaded_topic.data.@abs",
                        enabled: true,
                        timestampMethod: "receiveTime",
                        lineSize: 4,
                    },
                ],
            } }));
    },
    name: "preloaded data and its absolute value",
    parameters: {
        colorScheme: "light",
    },
};
export const LegendLeft = {
    render: function Story() {
        return (_jsx(PlotWrapper, { config: {
                ...exampleConfig,
                legendDisplay: "left",
                showPlotValuesInLegend: true,
                sidebarDimension: 440,
            } }));
    },
    parameters: {
        colorScheme: "light",
    },
};
export const LegendTop = {
    render: function Story() {
        return (_jsx(PlotWrapper, { config: {
                ...exampleConfig,
                legendDisplay: "top",
                showPlotValuesInLegend: true,
                sidebarDimension: 440,
            } }));
    },
    parameters: {
        colorScheme: "light",
    },
};
