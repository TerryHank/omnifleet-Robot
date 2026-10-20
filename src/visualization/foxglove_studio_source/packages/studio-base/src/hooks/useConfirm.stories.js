import { Fragment as _Fragment, jsx as _jsx } from "react/jsx-runtime";
import { useLayoutEffect } from "react";
import { useConfirm } from "./useConfirm";
export default {
    title: "hooks/useConfirm",
    parameters: { colorScheme: "dark" },
};
export const Defaults = {
    render: function Story() {
        const [confirm, confirmModal] = useConfirm();
        useLayoutEffect(() => {
            void confirm({
                title: "Example title",
            });
        }, [confirm]);
        return _jsx(_Fragment, { children: confirmModal });
    },
};
export const Primary = {
    render: function Story() {
        const [confirm, confirmModal] = useConfirm();
        useLayoutEffect(() => {
            void confirm({
                title: "Example title",
                prompt: "Example prompt",
                variant: "primary",
                ok: "Custom OK",
                cancel: "Continue anyway",
            });
        }, [confirm]);
        return _jsx(_Fragment, { children: confirmModal });
    },
};
export const PrimaryLight = { ...Primary, parameters: { colorScheme: "light" } };
export const Danger = {
    render: function Story() {
        const [confirm, confirmModal] = useConfirm();
        useLayoutEffect(() => {
            void confirm({
                title: "Example title",
                prompt: "Example prompt",
                variant: "danger",
                ok: "Destroy",
            });
        }, [confirm]);
        return _jsx(_Fragment, { children: confirmModal });
    },
};
export const DangerLight = { ...Danger, parameters: { colorScheme: "light" } };
