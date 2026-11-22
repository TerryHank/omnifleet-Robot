import { jsx as _jsx } from "react/jsx-runtime";
import { fireEvent, within } from "@storybook/testing-library";
import * as _ from "lodash-es";
import Stack from "@foxglove/studio-base/components/Stack";
import { Autocomplete } from "./Autocomplete";
export default {
    title: "components/Autocomplete",
    component: Autocomplete,
    parameters: { colorScheme: "dark" },
    args: {
        onSelect: () => { },
    },
    decorators: [
        (Story) => (_jsx(Stack, { padding: 2.5, children: _jsx(Story, {}) })),
    ],
};
const clickInput = async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const input = await canvas.findByTestId("autocomplete-textfield");
    fireEvent.click(input);
};
export const FilteringToO = {
    args: {
        items: ["one", "two", "three"],
        hasError: true,
        filterText: "o",
        value: "o",
    },
    name: "filtering to 'o'",
    play: clickInput,
};
export const FilteringToOLight = {
    ...FilteringToO,
    name: "filtering to 'o' light",
    parameters: { colorScheme: "light" },
};
export const UncontrolledValue = {
    args: {
        items: ["one", "two", "three"],
        filterText: "h",
        value: "h",
    },
    play: clickInput,
};
export const UncontrolledValueLight = {
    ...UncontrolledValue,
    parameters: { colorScheme: "light" },
};
export const SortWhenFilteringFalse = {
    args: {
        items: ["bab", "bb", "a2", "a1"],
        sortWhenFiltering: false,
        value: "b",
        filterText: "b",
    },
    name: "sortWhenFiltering=false",
    play: clickInput,
};
export const ManyItems = {
    args: {
        items: _.range(1, 1000).map((i) => `item_${i}`),
    },
    play: clickInput,
};
export const LongPathInPopup = {
    render: (args) => (_jsx("div", { style: { width: 200 }, children: _jsx(Autocomplete, { ...args }) })),
    args: {
        items: [
            "/abcdefghi_jklmnop.abcdefghi_jklmnop[:]{some_id==1297193}.isSomething",
            "/abcdefghi_jklmnop.abcdefghi_jklmnop[:]{some_id==1297194}.isSomething",
            "/abcdefghi_jklmnop.abcdefghi_jklmnop[:]{some_id==1297195}.isSomething",
        ],
        value: "/abcdefghi_jklmnop.abcdefghi_jklmnop[:]{some_id==1297193}.isSomething",
        filterText: "/abcdefghi_jklmnop.abcdefghi_jklmnop[:]{",
    },
    play: clickInput,
};
