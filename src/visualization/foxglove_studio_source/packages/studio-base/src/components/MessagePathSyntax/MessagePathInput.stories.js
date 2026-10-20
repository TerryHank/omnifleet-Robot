import { jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
//
// This file incorporates work covered by the following copyright and
// permission notice:
//
//   Copyright 2018-2021 Cruise LLC
//
//   This source code is licensed under the Apache License, Version 2.0,
//   found at http://www.apache.org/licenses/LICENSE-2.0
//   You may not use this file except in compliance with the License.
import { Stack } from "@mui/material";
import { fireEvent, screen, userEvent, waitFor, within } from "@storybook/testing-library";
import { useState } from "react";
import PanelSetup from "@foxglove/studio-base/stories/PanelSetup";
import { basicDatatypes } from "@foxglove/studio-base/util/basicDatatypes";
import MessagePathInput from "./MessagePathInput";
import { MessagePathInputStoryFixture } from "./fixture";
let manyTopics = [];
for (let i = 0; i < 10; i++) {
    manyTopics = manyTopics.concat(Array.from(basicDatatypes.keys()).map((schemaName) => ({ name: `/${schemaName.toLowerCase()}/${i}`, schemaName })));
}
const heavyFixture = {
    datatypes: basicDatatypes,
    topics: manyTopics,
    frame: {},
    globalVariables: { global_var_1: 42, global_var_2: 10 },
};
const clickInput = async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    fireEvent.click(await canvas.findByTestId("autocomplete-textfield"));
};
function MessagePathInputStory(props) {
    const [path, setPath] = useState(props.path);
    return (_jsx(PanelSetup, { fixture: props.heavy ?? false ? heavyFixture : MessagePathInputStoryFixture, children: _jsx(Stack, { direction: "row", flex: "auto", margin: 1.25, children: _jsx(MessagePathInput, { path: path, validTypes: props.validTypes, prioritizedDatatype: props.prioritizedDatatype, onChange: (newPath) => {
                    setPath(newPath);
                } }) }) }));
}
export default {
    title: "components/MessagePathInput",
    parameters: {
        colorScheme: "dark",
    },
};
export const PathWithHeaderFields = {
    render: MessagePathInputStory,
    args: { path: "/some_topic/state.header.stamp.sec" },
    play: clickInput,
};
export const AutocompleteTopics = {
    render: MessagePathInputStory,
    args: { path: "/" },
    play: clickInput,
};
export const AutocompleteScalarFromTopicAndEmptyPath = {
    render: MessagePathInputStory,
    args: { path: "", validTypes: ["int32"] },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        fireEvent.click(await canvas.findByTestId("autocomplete-textfield"));
        const options = await waitFor(() => screen.queryAllByTestId("autocomplete-item"));
        fireEvent.click(options[2]);
    },
};
export const AutocompleteScalarFromTopic = {
    render: MessagePathInputStory,
    args: { path: "", validTypes: ["int32"] },
    play: async ({ canvasElement }) => {
        const { keyboard } = userEvent.setup();
        const canvas = within(canvasElement);
        const input = await canvas.findByTestId("autocomplete-textfield");
        fireEvent.click(input);
        await keyboard("/some_logs_");
        const options = await waitFor(() => screen.queryAllByTestId("autocomplete-item"));
        fireEvent.click(options[1]);
    },
};
export const AutocompleteScalarFromFullTopic = {
    render: MessagePathInputStory,
    args: { path: "", validTypes: ["int32"] },
    play: async ({ canvasElement }) => {
        const { keyboard } = userEvent.setup();
        const canvas = within(canvasElement);
        const input = await canvas.findByTestId("autocomplete-textfield");
        fireEvent.click(input);
        await keyboard("/some_logs_topic");
        const options = await waitFor(() => screen.queryAllByTestId("autocomplete-item"));
        fireEvent.click(options[0]);
    },
};
export const AutocompleteWithFilterAndArraySuggestions = {
    render: MessagePathInputStory,
    args: { path: "stateitems" },
    play: clickInput,
};
export const AutocompleteMessagePath = {
    render: MessagePathInputStory,
    args: { path: "/some_topic/location.po" },
    name: "Autocomplete messagePath",
    play: clickInput,
};
export const AutocompleteMessagePathLight = {
    render: MessagePathInputStory,
    args: { path: "/some_topic/location.po" },
    name: "Autocomplete messagePath light",
    parameters: { colorScheme: "light" },
    play: clickInput,
};
export const AutocompleteFilter = {
    render: MessagePathInputStory,
    args: { path: "/some_topic/state.items[:]{}" },
    play: clickInput,
};
export const AutocompleteTopLevelFilter = {
    render: MessagePathInputStory,
    args: { path: "/some_topic/state{}" },
    play: clickInput,
};
export const AutocompleteForGlobalVariablesVariables = {
    render: MessagePathInputStory,
    args: { path: "/some_topic/state{foo_id==0}.items[:]{id==$}" },
    name: "Autocomplete for globalVariables variables",
    play: clickInput,
};
export const PathWithValidGlobalVariablesVariable = {
    render: MessagePathInputStory,
    args: { path: "/some_topic/state.items[:]{id==$global_var_2}" },
    name: "Path with valid globalVariables variable",
    play: clickInput,
};
export const PathWithInvalidGlobalVariablesVariable = {
    render: MessagePathInputStory,
    args: { path: "/some_topic/state.items[:]{id==$global_var_3}" },
    name: "Path with invalid globalVariables variable",
    play: clickInput,
};
export const PathWithIncorrectlyPrefixedGlobalVariablesVariable = {
    render: MessagePathInputStory,
    args: { path: "/some_topic/state.items[:]{id==global_var_2}" },
    name: "Path with incorrectly prefixed globalVariables variable",
    play: clickInput,
};
export const AutocompleteForPathWithGlobalVariablesVariableInSliceSingleIdx = {
    render: MessagePathInputStory,
    args: { path: "/some_topic/state.items[$]" },
    name: "Autocomplete for path with globalVariables variable in slice (single idx)",
    play: clickInput,
};
export const AutocompleteForPathWithGlobalVariablesVariableInSliceStartIdx = {
    render: MessagePathInputStory,
    args: { path: "/some_topic/state.items[$:]" },
    name: "Autocomplete for path with globalVariables variable in slice (start idx)",
    play: clickInput,
};
export const AutocompleteForPathWithGlobalVariablesVariableInSliceEndIdx = {
    render: MessagePathInputStory,
    args: { path: "/some_topic/state.items[:$]" },
    name: "Autocomplete for path with globalVariables variable in slice (end idx)",
    play: clickInput,
};
export const AutocompleteForPathWithGlobalVariablesVariablesInSliceStartAndEndIdx = {
    render: MessagePathInputStory,
    args: { path: "/some_topic/state.items[$global_var_2:$]" },
    name: "Autocomplete for path with globalVariables variables in slice (start and end idx)",
    play: clickInput,
};
export const PathWithInvalidMathModifier = {
    render: MessagePathInputStory,
    args: { path: "/some_topic/location.pose.x.@negative" },
    play: clickInput,
};
export const AutocompleteWhenPrioritizedDatatypeIsAvailable = {
    render: MessagePathInputStory,
    args: { path: "/", prioritizedDatatype: "msgs/State" },
    play: clickInput,
};
export const AutocompleteForPathWithExistingFilter = {
    render: MessagePathInputStory,
    args: { path: "/some_topic/state.items[:]{id==1}." },
    play: clickInput,
};
export const AutocompleteForPathWithExistingFilterUsingAGlobalVariable = {
    render: MessagePathInputStory,
    args: { path: "/some_topic/state.items[:]{id==$global_var_2}." },
    play: clickInput,
};
export const PerformanceTesting = {
    render: MessagePathInputStory,
    args: { path: ".", heavy: true },
    play: clickInput,
};
