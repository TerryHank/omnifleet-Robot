import { jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { action } from "@storybook/addon-actions";
import { PlayerCapabilities } from "@foxglove/studio-base/players/types";
import PanelSetup from "@foxglove/studio-base/stories/PanelSetup";
import TeleopPanel from "./index";
export default {
    title: "panels/Teleop",
    component: TeleopPanel,
    decorators: [
        (StoryComponent, context) => {
            return (_jsx(PanelSetup, { fixture: { capabilities: [PlayerCapabilities.advertise], publish: action("publish") }, includeSettings: context.parameters.includeSettings, children: _jsx(StoryComponent, {}) }));
        },
    ],
};
export const Unconfigured = {
    render: () => {
        return _jsx(TeleopPanel, {});
    },
};
export const WithSettings = {
    render: function Story() {
        return _jsx(TeleopPanel, { overrideConfig: { topic: "/abc" } });
    },
    parameters: {
        colorScheme: "light",
        includeSettings: true,
    },
};
export const WithTopic = {
    render: () => {
        return _jsx(TeleopPanel, { overrideConfig: { topic: "/abc" } });
    },
};
