import { jsx as _jsx } from "react/jsx-runtime";
import { useSnackbar } from "notistack";
import { useEffect } from "react";
import StudioToastProvider from "@foxglove/studio-base/components/StudioToastProvider";
export default {
    title: "components/StudioToastProvider",
    component: StudioToastProvider,
    parameters: {
        chromatic: {
            delay: 100,
        },
        colorScheme: "dark",
    },
    decorators: [
        (Wrapped) => {
            return (_jsx(StudioToastProvider, { children: _jsx(Wrapped, {}) }));
        },
    ],
};
export const OneError = {
    render: function Story() {
        const { enqueueSnackbar } = useSnackbar();
        useEffect(() => {
            enqueueSnackbar("Something bad happened", { variant: "error", persist: true });
        }, [enqueueSnackbar]);
        return _jsx(StudioToastProvider, {});
    },
};
export const OneWarning = {
    render: function Story() {
        const { enqueueSnackbar } = useSnackbar();
        useEffect(() => {
            enqueueSnackbar("This is the final countdown", { variant: "warning", persist: true });
        }, [enqueueSnackbar]);
        return _jsx(StudioToastProvider, {});
    },
};
export const OneInfo = {
    render: function Story() {
        const { enqueueSnackbar } = useSnackbar();
        useEffect(() => {
            enqueueSnackbar("This is the final countdown", { variant: "info", persist: true });
        }, [enqueueSnackbar]);
        return _jsx(StudioToastProvider, {});
    },
};
export const MultipleMessages = {
    render: function Story() {
        const { enqueueSnackbar } = useSnackbar();
        useEffect(() => {
            enqueueSnackbar("Something bad happened 1", { variant: "error", persist: true });
            enqueueSnackbar("Here's a helpful tip", { variant: "default", persist: true });
            enqueueSnackbar("Just a warning", { variant: "warning", persist: true });
            enqueueSnackbar("Great job!", { variant: "success", persist: true });
            enqueueSnackbar("Something happened 2", { variant: "info", persist: true });
        }, [enqueueSnackbar]);
        return _jsx(StudioToastProvider, {});
    },
};
export const MultipleMessagesLightTheme = {
    ...MultipleMessages,
    parameters: { colorScheme: "light" },
};
