import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import NotificationModal from "@foxglove/studio-base/components/NotificationModal";
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
    title: "components/NotificationModal",
};
export const ErrorNoSubtextWithDetails = {
    render: function Story() {
        return (_jsx(NotificationModal, { onRequestClose: () => { }, notification: {
                id: "1",
                message: "Error 1",
                details: fakeError(),
                created: new Date(),
                severity: "error",
            } }));
    },
    parameters: { colorScheme: "light" },
};
export const ErrorNoSubtextWithDetailsDark = {
    ...ErrorNoSubtextWithDetails,
    parameters: { colorScheme: "dark" },
};
export const ErrorWithSubtextAndDetails = {
    render: function Story() {
        return (_jsx(NotificationModal, { onRequestClose: () => { }, notification: {
                id: "1",
                message: "Error 1",
                details: fakeError(),
                created: new Date(),
                severity: "error",
                subText: "This error has a subtext.",
            } }));
    },
    parameters: { colorScheme: "light" },
};
export const ErrorWithSubtextNoDetails = {
    render: function Story() {
        return (_jsx(NotificationModal, { onRequestClose: () => { }, notification: {
                id: "1",
                message: "Error 1",
                details: undefined,
                created: new Date(),
                severity: "error",
                subText: "This error has a subtext.",
            } }));
    },
    parameters: { colorScheme: "light" },
};
export const Warning = {
    render: function Story() {
        return (_jsx(NotificationModal, { onRequestClose: () => { }, notification: {
                id: "1",
                message: "Warning 1",
                details: "Some error details",
                created: new Date(),
                severity: "warn",
            } }));
    },
    parameters: { colorScheme: "dark" },
};
export const ErrorNoDetailsOrSubtext = {
    render: function Story() {
        return (_jsx(NotificationModal, { onRequestClose: () => { }, notification: {
                id: "1",
                message: "Error 1",
                details: undefined,
                created: new Date(),
                severity: "error",
            } }));
    },
    parameters: { colorScheme: "dark" },
};
export const ErrorWithJsxElementDetails = {
    render: function Story() {
        return (_jsx(NotificationModal, { onRequestClose: () => { }, notification: {
                id: "1",
                message: "Error 1",
                details: (_jsxs("p", { children: ["This is ", _jsx("b", { style: { color: "red" }, children: "customized" }), " error detail."] })),
                created: new Date(),
                severity: "error",
            } }));
    },
    parameters: { colorScheme: "light" },
};
export const ErrorWithJsxElementDetailsDark = {
    ...ErrorWithJsxElementDetails,
    parameters: { colorScheme: "dark" },
};
export const ErrorWithNewlineDetails = {
    render: function Story() {
        return (_jsx(NotificationModal, { onRequestClose: () => { }, notification: {
                id: "1",
                message: "Error 1",
                details: "Some details.\n\nWith a newline.",
                created: new Date(),
                severity: "error",
            } }));
    },
    parameters: { colorScheme: "dark" },
};
