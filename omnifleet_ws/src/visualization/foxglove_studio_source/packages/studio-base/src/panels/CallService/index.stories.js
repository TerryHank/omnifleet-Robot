import { jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { expect } from "@storybook/jest";
import { userEvent, within } from "@storybook/testing-library";
import { PlayerCapabilities } from "@foxglove/studio-base/players/types";
import PanelSetup from "@foxglove/studio-base/stories/PanelSetup";
import delay from "@foxglove/studio-base/util/delay";
import CallServicePanel from "./index";
const successResponseJson = JSON.stringify({ success: true }, undefined, 2);
const baseConfig = {
    serviceName: "/set_bool",
    requestPayload: `{\n  "data": true\n}`,
};
const getFixture = ({ allowCallService }) => {
    const callService = async (service, _request) => {
        if (service !== baseConfig.serviceName) {
            throw new Error(`Service "${service}" does not exist`);
        }
        return { success: true };
    };
    return {
        datatypes: new Map(Object.entries({
            "std_srvs/SetBool_Request": { definitions: [{ name: "data", type: "bool" }] },
        })),
        frame: {},
        capabilities: allowCallService ? [PlayerCapabilities.callServices] : [],
        callService,
    };
};
export default {
    title: "panels/CallService",
    component: CallServicePanel,
    parameters: {
        colorScheme: "both-column",
    },
    decorators: [
        (StoryComponent, { parameters }) => {
            return (_jsx(PanelSetup, { fixture: parameters.panelSetup?.fixture, children: _jsx(StoryComponent, {}) }));
        },
    ],
};
export const Default = {
    render: () => {
        return _jsx(CallServicePanel, {});
    },
};
export const DefaultHorizontalLayout = {
    render: () => {
        return _jsx(CallServicePanel, { overrideConfig: { layout: "horizontal" } });
    },
};
export const CallServiceEnabled = {
    render: () => {
        return _jsx(CallServicePanel, {});
    },
    parameters: { panelSetup: { fixture: getFixture({ allowCallService: true }) } },
};
export const CallServiceEnabledServiceName = {
    render: () => {
        return _jsx(CallServicePanel, { overrideConfig: { ...baseConfig } });
    },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        const responseTextareas = await canvas.findAllByPlaceholderText("Response");
        const buttons = await canvas.findAllByTestId("call-service-button");
        buttons.forEach(async (button) => {
            await userEvent.click(button);
        });
        await delay(500);
        for (const textarea of responseTextareas) {
            await expect(textarea).toHaveValue(successResponseJson);
        }
    },
    parameters: { panelSetup: { fixture: getFixture({ allowCallService: true }) } },
};
export const CallServiceEnabledWithCustomButtonSettings = {
    render: () => {
        return (_jsx(CallServicePanel, { overrideConfig: {
                ...baseConfig,
                buttonColor: "#ffbf49",
                buttonTooltip: "I am a button tooltip",
                buttonText: "Call that funky service",
            } }));
    },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        const buttons = await canvas.findAllByText("Call that funky service");
        buttons.forEach(async (button) => {
            await userEvent.hover(button);
        });
    },
    parameters: { panelSetup: { fixture: getFixture({ allowCallService: true }) } },
};
const validJSON = `{\n  "a": 1,\n  "b": 2,\n  "c": 3\n}`;
export const WithValidJSON = {
    render: () => {
        return _jsx(CallServicePanel, { overrideConfig: { ...baseConfig, requestPayload: validJSON } });
    },
};
const invalidJSON = `{\n  "a": 1,\n  'b: 2,\n  "c": 3\n}`;
export const WithInvalidJSON = {
    render: () => {
        return _jsx(CallServicePanel, { overrideConfig: { ...baseConfig, requestPayload: invalidJSON } });
    },
};
export const CallingServiceThatDoesNotExist = {
    render: () => {
        return (_jsx(CallServicePanel, { overrideConfig: {
                ...baseConfig,
                serviceName: "/non_existing_service",
            } }));
    },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        const responseTextareas = await canvas.findAllByPlaceholderText("Response");
        const buttons = await canvas.findAllByTestId("call-service-button");
        buttons.forEach(async (button) => {
            await userEvent.click(button);
        });
        await delay(500);
        for (const textarea of responseTextareas) {
            await expect(textarea).toHaveValue(`Service "/non_existing_service" does not exist`);
        }
    },
    parameters: { panelSetup: { fixture: getFixture({ allowCallService: true }) } },
};
