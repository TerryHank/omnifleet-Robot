import { jsx as _jsx } from "react/jsx-runtime";
import { useEffect } from "react";
import SendNotificationToastAdapter from "@foxglove/studio-base/components/SendNotificationToastAdapter";
import StudioToastProvider from "@foxglove/studio-base/components/StudioToastProvider";
import sendNotification from "@foxglove/studio-base/util/sendNotification";
const fakeError = () => {
    const err = Error("This error is on purpose - it comes from the story");
    err.stack = `at http://localhost:49891/main.iframe.bundle.js:13051:22
      at finalStoryFn (http://localhost:49891/some_vendor_library-name_component-name-9a6f77.iframe.bundle.js:56275:32)
      at http://localhost:49891/some_vendor_library-name_component-name-9a6f77.iframe.bundle.js:53001:21
      at http://localhost:49891/some_vendor_library-name_component-name-9a6f77.iframe.bundle.js:54920:16
      at jsxDecorator (http://localhost:49891/some_vendor_library-name_component-name-9a6f77.iframe.bundle.js:48482:15)
      at http://localhost:49891/some_vendor_library-name_component-name-9a6f77.iframe.bundle.js:53001:21
      at http://localhost:49891/some_vendor_library-name_component-name-9a6f77.iframe.bundle.js:54884:12
      at http://localhost:49891/some_vendor_library-name_component-name-9a6f77.iframe.bundle.js:54920:16
      at withGrid (http://localhost:49891/some_vendor_library-name_component-name-9a6f77.iframe.bundle.js:45137:10)
      at http://localhost:49891/some_vendor_library-name_component-name-9a6f77.iframe.bundle.js:53001:21`;
    return err;
};
export default {
    title: "components/SendNotificationToastAdapter",
    component: SendNotificationToastAdapter,
    parameters: {
        chromatic: {
            delay: 100,
        },
        colorScheme: "dark",
    },
    decorators: [
        (Wrapped) => {
            return (_jsx("div", { style: { padding: 10, height: "300px" }, children: _jsx(StudioToastProvider, { children: _jsx(Wrapped, {}) }) }));
        },
    ],
};
export const OneError = {
    render: function Story() {
        useEffect(() => {
            sendNotification("Something bad happened", fakeError(), "app", "error");
        }, []);
        return _jsx(SendNotificationToastAdapter, {});
    },
};
export const OneWarning = {
    render: function Story() {
        useEffect(() => {
            sendNotification("This is the final countdown", "This warning is on purpose - it comes from the story", "app", "warn");
        }, []);
        return _jsx(SendNotificationToastAdapter, {});
    },
};
export const OneInfo = {
    render: function Story() {
        useEffect(() => {
            sendNotification("Here's a helpful tip", "These are the details of the message", "user", "info");
        }, []);
        return _jsx(SendNotificationToastAdapter, {});
    },
};
export const MultipleMessages = {
    render: function Story() {
        useEffect(() => {
            sendNotification("Something bad happened 1", fakeError(), "app", "error");
            sendNotification("Here's a helpful tip", fakeError(), "user", "info");
            sendNotification("Just a warning", "This warning is on purpose - it comes from the story", "app", "warn");
            sendNotification("Something bad happened 2", fakeError(), "app", "error");
        }, []);
        return _jsx(SendNotificationToastAdapter, {});
    },
};
export const MultipleMessagesLightTheme = {
    ...MultipleMessages,
    parameters: { colorScheme: "light" },
};
