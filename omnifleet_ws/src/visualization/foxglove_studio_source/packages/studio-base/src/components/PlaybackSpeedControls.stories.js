import { jsx as _jsx } from "react/jsx-runtime";
import { screen, userEvent } from "@storybook/testing-library";
import MockMessagePipelineProvider from "@foxglove/studio-base/components/MessagePipeline/MockMessagePipelineProvider";
import PlaybackSpeedControls from "@foxglove/studio-base/components/PlaybackSpeedControls";
import MockCurrentLayoutProvider from "@foxglove/studio-base/providers/CurrentLayoutProvider/MockCurrentLayoutProvider";
const CAPABILITIES = ["setSpeed", "playbackControl"];
export default {
    title: "components/PlaybackSpeedControls",
    component: PlaybackSpeedControls,
    parameters: { colorScheme: "dark" },
    decorators: [
        (WrappedStory, { args }) => (_jsx(MockCurrentLayoutProvider, { children: _jsx(MockMessagePipelineProvider, { ...args, children: _jsx("div", { style: { padding: 20, paddingTop: 300 }, children: _jsx(WrappedStory, {}) }) }) })),
    ],
    play: async () => {
        const el = await screen.findByTestId("PlaybackSpeedControls-Dropdown");
        if (!el.disabled) {
            await userEvent.click(el);
        }
    },
};
export const WithoutSpeedCapability = {
    name: "without speed capability",
};
export const WithoutASpeedFromThePlayer = {
    name: "without a speed from the player",
    args: { capabilities: CAPABILITIES, activeData: { speed: undefined } },
};
export const WithASpeed = {
    name: "with a speed",
    args: { capabilities: CAPABILITIES },
};
export const WithAVerySmallSpeed = {
    name: "with a very small speed",
    args: { capabilities: CAPABILITIES, activeData: { speed: 0.01 } },
};
