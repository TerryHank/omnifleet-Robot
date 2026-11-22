import { jsx as _jsx } from "react/jsx-runtime";
import { screen, userEvent } from "@storybook/testing-library";
import MockMessagePipelineProvider from "@foxglove/studio-base/components/MessagePipeline/MockMessagePipelineProvider";
import EventsProvider from "@foxglove/studio-base/providers/EventsProvider";
import { CreateEventDialog } from "./CreateEventDialog";
export default {
    component: CreateEventDialog,
    title: "components/CreateEventDialog",
    args: { onClose: () => { } },
    decorators: [
        (Wrapped) => {
            return (_jsx(EventsProvider, { children: _jsx(MockMessagePipelineProvider, { children: _jsx(Wrapped, {}) }) }));
        },
    ],
    parameters: {
        colorScheme: "light",
    },
};
export const Empty = {};
export const Normal = {
    play: async () => {
        const { click, keyboard } = userEvent.setup();
        const firstKey = await screen.findByPlaceholderText("Key (string)");
        await click(firstKey);
        await keyboard("1");
        const firstValue = await screen.findByPlaceholderText("Value (string)");
        await click(firstValue);
        await keyboard("2");
        const firstPlus = await screen.findByTestId("add");
        await click(firstPlus);
        const secondKey = await screen.findAllByPlaceholderText("Key (string)");
        await click(secondKey[1]);
        await keyboard("3");
        const secondValue = await screen.findAllByPlaceholderText("Value (string)");
        await click(secondValue[1]);
        await keyboard("4");
    },
};
export const WithDuplicates = {
    play: async () => {
        const { click, keyboard } = userEvent.setup();
        const firstKey = await screen.findByPlaceholderText("Key (string)");
        await click(firstKey);
        await keyboard("1");
        const firstValue = await screen.findByPlaceholderText("Value (string)");
        await click(firstValue);
        await keyboard("2");
        const firstPlus = await screen.findByTestId("add");
        await click(firstPlus);
        const secondKey = await screen.findAllByPlaceholderText("Key (string)");
        await click(secondKey[1]);
        await keyboard("1");
        const secondValue = await screen.findAllByPlaceholderText("Value (string)");
        await click(secondValue[1]);
        await keyboard("2");
    },
};
