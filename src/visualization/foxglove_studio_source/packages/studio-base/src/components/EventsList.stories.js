import { jsx as _jsx } from "react/jsx-runtime";
import { screen, userEvent } from "@storybook/testing-library";
import { useEffect } from "react";
import MockMessagePipelineProvider from "@foxglove/studio-base/components/MessagePipeline/MockMessagePipelineProvider";
import { useEvents } from "@foxglove/studio-base/context/EventsContext";
import EventsProvider from "@foxglove/studio-base/providers/EventsProvider";
import { makeMockEvents } from "@foxglove/studio-base/test/mocks/makeMockEvents";
import { EventsList } from "./EventsList";
function Wrapper(Child) {
    return (_jsx(MockMessagePipelineProvider, { children: _jsx(EventsProvider, { children: _jsx(Child, {}) }) }));
}
export default {
    title: "components/EventsList",
    component: EventsList,
    decorators: [Wrapper],
};
export const Default = {
    render: function Story() {
        const setEvents = useEvents((store) => store.setEvents);
        useEffect(() => {
            setEvents({ loading: false, value: makeMockEvents(20) });
        }, [setEvents]);
        return _jsx(EventsList, {});
    },
};
export const Selected = {
    render: function Story() {
        const setEvents = useEvents((store) => store.setEvents);
        const selectEvent = useEvents((store) => store.selectEvent);
        useEffect(() => {
            const events = makeMockEvents(20);
            setEvents({ loading: false, value: events });
        }, [selectEvent, setEvents]);
        return _jsx(EventsList, {});
    },
    play: async () => {
        const events = await screen.findAllByTestId("sidebar-event");
        await userEvent.click(events[1]);
    },
    parameters: {
        colorScheme: "light",
    },
};
export const WithError = {
    render: function Story() {
        const setEvents = useEvents((store) => store.setEvents);
        useEffect(() => {
            setEvents({ loading: false, error: new Error("Error loading events") });
        }, [setEvents]);
        return _jsx(EventsList, {});
    },
};
export const Loading = {
    render: function Story() {
        const setEvents = useEvents((store) => store.setEvents);
        useEffect(() => {
            setEvents({ loading: true });
        }, [setEvents]);
        return _jsx(EventsList, {});
    },
};
