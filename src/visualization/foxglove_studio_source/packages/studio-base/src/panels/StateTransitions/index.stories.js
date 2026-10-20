import { jsx as _jsx } from "react/jsx-runtime";
import { produce } from "immer";
import { useCallback } from "react";
import Stack from "@foxglove/studio-base/components/Stack";
import PanelSetup from "@foxglove/studio-base/stories/PanelSetup";
import { useReadySignal } from "@foxglove/studio-base/stories/ReadySignalContext";
import { expandedLineColors } from "@foxglove/studio-base/util/plotColors";
import StateTransitions from "./index";
const systemStateMessages = [
    { header: { stamp: { sec: 1526191539, nsec: 574635076 } }, state: 0 },
    { header: { stamp: { sec: 1526191539, nsec: 673758203 } }, state: 0 },
    { header: { stamp: { sec: 1526191539, nsec: 770527187 } }, state: 1 },
    { header: { stamp: { sec: 1526191539, nsec: 871076484 } }, state: 1 },
    { header: { stamp: { sec: 1526191539, nsec: 995802312 } }, state: 1 },
    { header: { stamp: { sec: 1526191540, nsec: 81700551 } }, state: 1 },
    { header: { stamp: { sec: 1526191540, nsec: 184463111 } }, state: 1 },
    { header: { stamp: { sec: 1526191540, nsec: 285808851 } }, state: 2 },
    { header: { stamp: { sec: 1526191540, nsec: 371183619 } }, state: 2 },
    { header: { stamp: { sec: 1526191540, nsec: 479369260 } }, state: 2 },
    { header: { stamp: { sec: 1526191540, nsec: 587095370 } }, state: 2 },
    { header: { stamp: { sec: 1526191540, nsec: 685730694 } }, state: 2 },
    { header: { stamp: { sec: 1526191540, nsec: 785737230 } }, state: 2 },
    { header: { stamp: { sec: 1526191540, nsec: 869057829 } }, state: 2 },
    { header: { stamp: { sec: 1526191540, nsec: 984145879 } }, state: 2 },
    { header: { stamp: { sec: 1526191541, nsec: 85765716 } }, state: 2 },
    { header: { stamp: { sec: 1526191541, nsec: 182717960 } }, state: 3 },
    { header: { stamp: { sec: 1526191541, nsec: 286998440 } }, state: 3 },
    { header: { stamp: { sec: 1526191541, nsec: 370689856 } }, state: 3 },
    { header: { stamp: { sec: 1526191541, nsec: 483672422 } }, state: -1 },
    { header: { stamp: { sec: 1526191541, nsec: 578787057 } }, state: -1 },
    { header: { stamp: { sec: 1526191541, nsec: 677515597 } }, state: -1 },
    { header: { stamp: { sec: 1526191541, nsec: 789110904 } }, state: -1 },
];
const fixture = {
    datatypes: new Map(Object.entries({
        "msgs/SystemState": {
            definitions: [
                { type: "std_msgs/Header", name: "header", isArray: false, isComplex: true },
                { type: "int8", name: "UNKNOWN", isConstant: true, value: -1 },
                { type: "int8", name: "OFF", isConstant: true, value: 1 },
                { type: "int8", name: "BOOTING", isConstant: true, value: 2 },
                { type: "int8", name: "ACTIVE", isConstant: true, value: 3 },
                { type: "int8", name: "state", isArray: false },
                { type: "msgs/DataValue", name: "data", isArray: false, isComplex: true },
            ],
        },
        "std_msgs/Header": {
            definitions: [
                { name: "seq", type: "uint32", isArray: false },
                {
                    name: "stamp",
                    type: "time",
                    isArray: false,
                },
                { name: "frame_id", type: "string", isArray: false },
            ],
        },
        "msgs/DataValue": {
            definitions: [{ type: "string", name: "value", isArray: false, isComplex: false }],
        },
    })),
    topics: [
        { name: "/some/topic/with/state", schemaName: "msgs/SystemState" },
        { name: "/some/topic/with/string_state", schemaName: "msgs/SystemState" },
        { name: "/blocks", schemaName: "msgs/SystemState" },
    ],
    activeData: {
        startTime: { sec: 1526191539, nsec: 202050 },
        endTime: { sec: 1526191542, nsec: 999997069 },
        isPlaying: false,
        speed: 0.2,
    },
    frame: {
        "/some/topic/with/state": systemStateMessages.map((message, idx) => ({
            topic: "/some/topic/with/state",
            receiveTime: message.header.stamp,
            message: { ...message, data: { value: idx } },
            schemaName: "msgs/SystemState",
            sizeInBytes: 0,
        })),
        "/some/topic/with/string_state": systemStateMessages.map((message, idx) => {
            const values = "abcdefghijklmnopqrstuvwxyz".split("");
            return {
                topic: "/some/topic/with/string_state",
                receiveTime: message.header.stamp,
                message: { ...message, data: { value: values[idx % values.length] } },
                schemaName: "msgs/SystemState",
                sizeInBytes: 0,
            };
        }),
    },
};
export default {
    title: "panels/StateTransitions",
    component: StateTransitions,
    parameters: {
        colorScheme: "light",
        chromatic: { delay: 100 },
    },
};
export const Empty = {
    render: function Story() {
        const readySignal = useReadySignal({ count: 1 });
        const pauseFrame = useCallback(() => readySignal, [readySignal]);
        return (_jsx(PanelSetup, { fixture: fixture, pauseFrame: pauseFrame, children: _jsx(StateTransitions, {}) }));
    },
    play: async ({ parameters }) => {
        await parameters.storyReady;
    },
    parameters: { useReadySignal: true, colorScheme: "light" },
};
export const ColorPalette = {
    render: () => (_jsx(Stack, { padding: 2, fullWidth: true, children: expandedLineColors.map((color) => (_jsx("div", { style: { backgroundColor: color, height: "1rem" } }, color))) })),
};
export const CloseValues = {
    render: function Story() {
        const readySignal = useReadySignal({ count: 1 });
        const pauseFrame = useCallback(() => readySignal, [readySignal]);
        const closeMessages = [
            { header: { stamp: { sec: 0, nsec: 0 } }, state: 0 },
            { header: { stamp: { sec: 0, nsec: 0 } }, state: 1 },
            { header: { stamp: { sec: 0, nsec: 0 } }, state: 2 },
            { header: { stamp: { sec: 0, nsec: 0 } }, state: 3 },
            { header: { stamp: { sec: 0, nsec: 0 } }, state: 4 },
            { header: { stamp: { sec: 100, nsec: 0 } }, state: 4 },
        ];
        const closeFixture = produce(fixture, (draft) => {
            draft.activeData = {
                startTime: { sec: 0, nsec: 0 },
                endTime: { sec: 100, nsec: 0 },
                isPlaying: false,
                speed: 0.2,
            };
            draft.frame = {
                "/some/topic/with/state": closeMessages.map((message) => ({
                    topic: "/some/topic/with/state",
                    receiveTime: message.header.stamp,
                    message,
                    schemaName: "msgs/SystemState",
                    sizeInBytes: 0,
                })),
            };
        });
        return (_jsx(PanelSetup, { fixture: closeFixture, pauseFrame: pauseFrame, children: _jsx(StateTransitions, { overrideConfig: {
                    paths: [{ value: "/some/topic/with/state.state", timestampMethod: "receiveTime" }],
                    isSynced: true,
                } }) }));
    },
    play: async ({ parameters }) => {
        await parameters.storyReady;
    },
    parameters: {
        colorScheme: "light",
        useReadySignal: true,
    },
};
export const OnePath = {
    render: function Story() {
        const readySignal = useReadySignal({ count: 1 });
        const pauseFrame = useCallback(() => readySignal, [readySignal]);
        return (_jsx(PanelSetup, { fixture: fixture, pauseFrame: pauseFrame, children: _jsx(StateTransitions, { overrideConfig: {
                    paths: [{ value: "/some/topic/with/state.state", timestampMethod: "receiveTime" }],
                    isSynced: true,
                } }) }));
    },
    play: async ({ parameters }) => {
        await parameters.storyReady;
    },
    parameters: { useReadySignal: true, colorScheme: "light" },
};
export const WithXAxisMinMax = {
    render: function Story() {
        const readySignal = useReadySignal({ count: 1 });
        const pauseFrame = useCallback(() => readySignal, [readySignal]);
        return (_jsx(PanelSetup, { fixture: fixture, pauseFrame: pauseFrame, includeSettings: true, children: _jsx(StateTransitions, { overrideConfig: {
                    xAxisMinValue: 1,
                    xAxisMaxValue: 3,
                    paths: [{ value: "/some/topic/with/state.state", timestampMethod: "receiveTime" }],
                    isSynced: true,
                } }) }));
    },
    play: async ({ parameters }) => {
        await parameters.storyReady;
    },
    parameters: { colorScheme: "light", useReadySignal: true },
};
export const WithXAxisRange = {
    render: function Story() {
        const readySignal = useReadySignal({ count: 1 });
        const pauseFrame = useCallback(() => readySignal, [readySignal]);
        const ourFixture = produce(fixture, (draft) => {
            draft.activeData.currentTime = systemStateMessages.at(-1)?.header.stamp;
        });
        return (_jsx(PanelSetup, { fixture: ourFixture, pauseFrame: pauseFrame, includeSettings: true, children: _jsx(StateTransitions, { overrideConfig: {
                    xAxisRange: 3,
                    paths: [{ value: "/some/topic/with/state.state", timestampMethod: "receiveTime" }],
                    isSynced: true,
                } }) }));
    },
    play: async ({ parameters }) => {
        await parameters.storyReady;
    },
    parameters: { colorScheme: "light", useReadySignal: true },
};
export const WithSettings = {
    render: function Story() {
        const readySignal = useReadySignal({ count: 1 });
        const pauseFrame = useCallback(() => readySignal, [readySignal]);
        return (_jsx(PanelSetup, { fixture: fixture, pauseFrame: pauseFrame, includeSettings: true, children: _jsx(StateTransitions, { overrideConfig: {
                    paths: [{ value: "/some/topic/with/state.state", timestampMethod: "receiveTime" }],
                    isSynced: true,
                } }) }));
    },
    play: async ({ parameters }) => {
        await parameters.storyReady;
    },
    parameters: { useReadySignal: true, colorScheme: "light" },
};
export const MultiplePaths = {
    render: function Story() {
        const readySignal = useReadySignal({ count: 1 });
        const pauseFrame = useCallback(() => readySignal, [readySignal]);
        return (_jsx(PanelSetup, { fixture: fixture, pauseFrame: pauseFrame, children: _jsx(StateTransitions, { overrideConfig: {
                    paths: new Array(5).fill({
                        value: "/some/topic/with/state.state",
                        timestampMethod: "receiveTime",
                    }),
                    isSynced: true,
                } }) }));
    },
    play: async ({ parameters }) => {
        await parameters.storyReady;
    },
    parameters: { useReadySignal: true, colorScheme: "light" },
};
export const LongPath = {
    render: function Story() {
        const readySignal = useReadySignal({ count: 1 });
        const pauseFrame = useCallback(() => readySignal, [readySignal]);
        return (_jsx(PanelSetup, { fixture: fixture, pauseFrame: pauseFrame, style: { maxWidth: 100 }, children: _jsx(StateTransitions, { overrideConfig: {
                    paths: [{ value: "/some/topic/with/state.state", timestampMethod: "receiveTime" }],
                    isSynced: true,
                } }) }));
    },
    play: async ({ parameters }) => {
        await parameters.storyReady;
    },
    parameters: { useReadySignal: true, colorScheme: "light" },
};
export const ColorClash = {
    render: function Story() {
        const readySignal = useReadySignal({ count: 1 });
        const pauseFrame = useCallback(() => readySignal, [readySignal]);
        return (_jsx(PanelSetup, { fixture: fixture, pauseFrame: pauseFrame, children: _jsx(StateTransitions, { overrideConfig: {
                    paths: [
                        { value: "/some/topic/with/string_state.data.value", timestampMethod: "receiveTime" },
                    ],
                    isSynced: true,
                } }) }));
    },
    play: async ({ parameters }) => {
        await parameters.storyReady;
    },
    parameters: { useReadySignal: true, colorScheme: "light" },
};
const messageCache = {
    blocks: [
        {
            sizeInBytes: 0,
            messagesByTopic: {
                "/blocks": systemStateMessages.slice(0, 5).map((message, idx) => ({
                    topic: "/blocks",
                    receiveTime: message.header.stamp,
                    message: { ...message, data: { value: idx } },
                    schemaName: "msgs/SystemState",
                    sizeInBytes: 0,
                })),
            },
        },
        {
            sizeInBytes: 0,
            messagesByTopic: {
                "/blocks": systemStateMessages.slice(7, 12).map((message, idx) => ({
                    topic: "/blocks",
                    receiveTime: message.header.stamp,
                    message: { ...message, data: { value: idx } },
                    schemaName: "msgs/SystemState",
                    sizeInBytes: 0,
                })),
            },
        },
        {
            sizeInBytes: 0,
            messagesByTopic: {},
        },
        {
            sizeInBytes: 0,
            messagesByTopic: {
                "/blocks": systemStateMessages.slice(15, 19).map((message, idx) => ({
                    topic: "/blocks",
                    receiveTime: message.header.stamp,
                    message: { ...message, data: { value: idx } },
                    schemaName: "msgs/SystemState",
                    sizeInBytes: 0,
                })),
            },
        },
    ],
    startTime: systemStateMessages[0].header.stamp,
};
export const Blocks = {
    render: function Story() {
        const readySignal = useReadySignal({ count: 1 });
        const pauseFrame = useCallback(() => readySignal, [readySignal]);
        return (_jsx(PanelSetup, { fixture: { ...fixture, progress: { messageCache } }, pauseFrame: pauseFrame, children: _jsx(StateTransitions, { overrideConfig: {
                    paths: [
                        { value: "/some/topic/with/state.state", timestampMethod: "receiveTime" },
                        { value: "/blocks.state", timestampMethod: "receiveTime" },
                        { value: "/blocks.state", timestampMethod: "receiveTime" },
                    ],
                    isSynced: true,
                } }) }));
    },
    play: async ({ parameters }) => {
        await parameters.storyReady;
    },
    parameters: { useReadySignal: true, colorScheme: "light" },
};
