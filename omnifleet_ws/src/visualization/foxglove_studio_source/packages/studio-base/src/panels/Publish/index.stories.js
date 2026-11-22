import { jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { action } from "@storybook/addon-actions";
import { expect } from "@storybook/jest";
import { userEvent, within } from "@storybook/testing-library";
import Publish from "@foxglove/studio-base/panels/Publish";
import { PlayerCapabilities } from "@foxglove/studio-base/players/types";
import PanelSetup from "@foxglove/studio-base/stories/PanelSetup";
const getFixture = ({ allowPublish }) => {
    return {
        topics: [{ name: "/sample_topic", schemaName: "std_msgs/String" }],
        datatypes: new Map(Object.entries({ "std_msgs/String": { definitions: [{ name: "data", type: "string" }] } })),
        frame: {},
        capabilities: allowPublish ? [PlayerCapabilities.advertise] : [],
        publish: action("publish"),
        setPublishers: action("setPublishers"),
    };
};
const emptyFixture = {
    topics: [],
    datatypes: new Map(),
    frame: {},
    capabilities: [PlayerCapabilities.advertise],
};
const advancedJSON = `{\n  "data": ""\n}`;
const baseConfig = {
    topicName: "/sample_topic",
    datatype: "std_msgs/String",
    advancedView: true,
    value: advancedJSON,
};
export default {
    title: "panels/Publish",
    component: Publish,
    args: {
        allowPublish: false,
        includeSettings: true,
        isEmpty: false,
    },
    parameters: {
        colorScheme: "both-column",
    },
    decorators: [
        (Story, ctx) => {
            const { args: { allowPublish, includeSettings, isEmpty, ...args }, } = ctx;
            return (_jsx(PanelSetup, { includeSettings: includeSettings, fixture: isEmpty ? emptyFixture : getFixture({ allowPublish }), children: _jsx(Story, { args }) }));
        },
    ],
};
export const Default = {};
export const PublishEnabled = {
    args: { allowPublish: true },
};
export const WhenSelectingATopicSchemaIsSuggested = {
    args: { allowPublish: true },
    name: "When selecting a topic schema is suggested",
    play: async ({ canvasElement, step }) => {
        const { keyboard, type } = userEvent.setup();
        const canvas = within(canvasElement);
        const inputs = await canvas.findAllByRole("combobox");
        const topicInput = inputs[0];
        const schemaInput = inputs[1];
        const valueTextarea = await canvas.findByPlaceholderText("Enter message content as JSON");
        await step("Select a topic", async () => {
            await type(topicInput, "/sample_");
            await keyboard("[ArrowDown]");
            await keyboard("[Enter]");
        });
        await expect(topicInput).toHaveValue("/sample_topic");
        await expect(valueTextarea).toHaveValue(advancedJSON);
        await expect(schemaInput).toHaveValue("std_msgs/String");
    },
    parameters: { colorScheme: "light" },
};
export const PublishEnabledWithTopicAndSchema = {
    args: {
        allowPublish: true,
        overrideConfig: { ...baseConfig },
    },
    name: "Publish Enabled with topic and schema",
};
export const PublishEnabledWithCustomButtonSettings = {
    args: {
        allowPublish: true,
        overrideConfig: {
            ...baseConfig,
            buttonColor: "#ffbf49",
            buttonTooltip: "I am a button tooltip",
            buttonText: "Send message",
        },
    },
    name: "Publish Enabled with custom button settings",
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        const buttons = await canvas.findAllByText("Send message");
        buttons.forEach(async (button) => {
            await userEvent.hover(button);
        });
    },
};
export const PublishDisabledWithTopicAndSchema = {
    args: {
        allowPublish: false,
        overrideConfig: {
            ...baseConfig,
        },
    },
    name: "Publish Disabled with topic and schema",
};
const validJSON = `{\n  "a": 1,\n  "b": 2,\n  "c": 3\n}`;
export const WithValidJSON = {
    args: {
        allowPublish: true,
        overrideConfig: {
            ...baseConfig,
            value: validJSON,
        },
    },
    name: "Publish Enabled with valid JSON",
};
const invalidJSON = `{\n  "a": 1,\n  'b: 2,\n  "c": 3\n}`;
export const WithInvalidJSON = {
    args: {
        allowPublish: true,
        overrideConfig: {
            ...baseConfig,
            value: invalidJSON,
        },
    },
    name: "Publish Enabled with invalid JSON",
};
export const WithSchemaThatNoLongerExists = {
    args: {
        allowPublish: true,
        isEmpty: true,
        overrideConfig: {
            ...baseConfig,
            advancedView: true,
        },
    },
    name: "Publish Enabled with schema that no longer exists",
};
export const DefaultEditingModeOff = {
    args: { overrideConfig: { advancedView: false } },
    name: "Default (editing mode off)",
};
export const PublishEnabledEditingOff = {
    args: {
        allowPublish: true,
        overrideConfig: { advancedView: false },
    },
    name: "Publish Enabled (editing mode off)",
};
export const PublishEnabledWithTopicAndSchemaEditingOff = {
    args: {
        allowPublish: true,
        overrideConfig: {
            ...baseConfig,
            advancedView: false,
        },
    },
    name: "Publish Enabled with topic and schema (editing mode off)",
};
export const PublishEnabledWithCustomButtonSettingsEditingOff = {
    args: {
        allowPublish: true,
        overrideConfig: {
            ...baseConfig,
            buttonColor: "#ffbf49",
            buttonText: "Send message",
            buttonTooltip: "I am a button tooltip",
            advancedView: false,
        },
    },
    name: "Publish Enabled with custom button settings (editing mode off)",
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        const buttons = await canvas.findAllByText("Send message");
        buttons.forEach(async (button) => {
            await userEvent.hover(button);
        });
    },
};
export const PublishDisabledEditingModeOff = {
    args: {
        overrideConfig: {
            ...baseConfig,
            advancedView: false,
        },
    },
    name: "Publish Disabled (editing mode off)",
};
