import { jsx as _jsx } from "react/jsx-runtime";
import { fireEvent, userEvent, within } from "@storybook/testing-library";
import Table from "@foxglove/studio-base/panels/Table";
import { mockMessage } from "@foxglove/studio-base/players/TopicAliasingPlayer/mocks";
import PanelSetup from "@foxglove/studio-base/stories/PanelSetup";
const makeArrayData = ({ length = 50, nestArray = true, } = {}) => {
    return new Array(length).fill(0).map((_, i) => {
        return {
            val: i,
            bool: true,
            str: `${i}-abcd-edfg`,
            n: null, // eslint-disable-line no-restricted-syntax
            u: undefined,
            obj: {
                date: new Date(`2020-01-${i}`),
            },
            arr: nestArray ? makeArrayData({ length: 5, nestArray: false }) : [],
            primitiveArray: [1, 2, 3, 4, 5],
            typedArray: new Uint32Array([0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a]),
        };
    });
};
const fixture = {
    datatypes: new Map(Object.entries({
        arr_item: {
            definitions: [
                { type: "int32", name: "val", isConstant: false, isArray: false },
                { type: "int32", name: "primitiveArray", isConstant: false, isArray: true },
            ],
        },
        my_arr: {
            definitions: [
                { type: "arr_item", name: "array", isConstant: false, isArray: true, isComplex: true },
            ],
        },
    })),
    topics: [{ name: "/my_arr", schemaName: "my_arr" }],
    frame: {
        "/my_arr": [
            {
                topic: "/my_arr",
                receiveTime: { sec: 1, nsec: 0 },
                message: { array: makeArrayData() },
                schemaName: "my_arr",
                sizeInBytes: 0,
            },
        ],
    },
};
const longTextFixture = {
    datatypes: new Map([
        [
            "schema",
            {
                definitions: [
                    { type: "string", name: "value_a", isConstant: false, isArray: false },
                    { type: "string", name: "value_b", isConstant: false, isArray: false },
                ],
            },
        ],
    ]),
    topics: [{ name: "topic", schemaName: "schema" }],
    frame: {
        topic: [
            mockMessage({
                value_a: Array(30).fill("Long string that could wrap.").join(" \n"),
                value_b: "Another value",
            }, { topic: "topic" }),
        ],
    },
};
export default {
    title: "panels/Table",
};
export const NoTopicPath = {
    render: () => (_jsx(PanelSetup, { fixture: { frame: {}, topics: [] }, children: _jsx(Table, { overrideConfig: { topicPath: "" } }) })),
};
export const NoData = {
    render: () => (_jsx(PanelSetup, { fixture: { frame: {}, topics: [] }, children: _jsx(Table, { overrideConfig: { topicPath: "/unknown" } }) })),
};
export const LongTextValue = {
    render: () => (_jsx(PanelSetup, { fixture: longTextFixture, children: _jsx(Table, { overrideConfig: { topicPath: "topic" } }) })),
};
export const Arrays = {
    render: () => (_jsx(PanelSetup, { fixture: fixture, children: _jsx(Table, { overrideConfig: { topicPath: "/my_arr.array" } }) })),
};
export const ExpandRows = {
    render: () => (_jsx(PanelSetup, { fixture: fixture, children: _jsx(Table, { overrideConfig: { topicPath: "/my_arr.array" } }) })),
    parameters: { colorScheme: "dark" },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        const [target] = await canvas.findAllByTestId("expand-row-0");
        fireEvent.click(target);
    },
};
export const ExpandCellsWithNestedObjects = {
    render: () => (_jsx(PanelSetup, { fixture: fixture, children: _jsx(Table, { overrideConfig: { topicPath: "/my_arr.array" } }) })),
    parameters: { colorScheme: "dark" },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        const [target] = await canvas.findAllByTestId("expand-cell-obj-0");
        fireEvent.click(target);
    },
};
export const ExpandCellsWithNestedArrays = {
    render: () => (_jsx(PanelSetup, { fixture: fixture, children: _jsx(Table, { overrideConfig: { topicPath: "/my_arr.array" } }) })),
    parameters: { colorScheme: "dark" },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        const [target] = await canvas.findAllByTestId("expand-cell-arr-0");
        fireEvent.click(target);
    },
};
export const ExpandNestedCells = {
    render: () => (_jsx(PanelSetup, { fixture: fixture, children: _jsx(Table, { overrideConfig: { topicPath: "/my_arr.array" } }) })),
    parameters: { colorScheme: "dark" },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        const [targetRow] = await canvas.findAllByTestId("expand-row-0");
        fireEvent.click(targetRow);
        const nestedRows = await canvas.findAllByTestId("expand-row-0");
        fireEvent.click(nestedRows[2]);
    },
};
export const ExpandMultipleRows = {
    render: () => (_jsx(PanelSetup, { fixture: fixture, children: _jsx(Table, { overrideConfig: { topicPath: "/my_arr.array" } }) })),
    parameters: { colorScheme: "dark" },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        const [row1] = await canvas.findAllByTestId("expand-row-0");
        fireEvent.click(row1);
        const [row2] = await canvas.findAllByTestId("expand-row-1");
        fireEvent.click(row2);
    },
};
export const Filtering = {
    render: () => (_jsx(PanelSetup, { fixture: fixture, children: _jsx(Table, { overrideConfig: { topicPath: "/my_arr.array[:]{val==3}" } }) })),
};
export const Sorting = {
    render: () => (_jsx(PanelSetup, { fixture: fixture, children: _jsx(Table, { overrideConfig: { topicPath: "/my_arr.array" } }) })),
    parameters: { colorScheme: "dark" },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        const [targetCol] = await canvas.findAllByTestId("column-header-val");
        await userEvent.click(targetCol);
    },
};
export const HandlesPrimitives = {
    render: () => (_jsx(PanelSetup, { fixture: fixture, children: _jsx(Table, { overrideConfig: { topicPath: "/my_arr.array[:].val" } }) })),
};
export const HandlesArraysOfPrimitives = {
    render: () => (_jsx(PanelSetup, { fixture: fixture, children: _jsx(Table, { overrideConfig: { topicPath: "/my_arr.array[:].primitiveArray" } }) })),
};
export const ConstrainedWidth = {
    render: () => (_jsx(PanelSetup, { fixture: fixture, children: _jsx("div", { style: { width: "100px" }, children: _jsx(Table, { overrideConfig: { topicPath: "/my_arr.array[:]{val==3}" } }) }) })),
};
