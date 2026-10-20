import { jsx as _jsx } from "react/jsx-runtime";
import { fireEvent, screen } from "@storybook/testing-library";
import { ShareJsonModal, } from "@foxglove/studio-base/components/ShareJsonModal";
export default {
    title: "components/ShareJsonModal",
};
const sharedProps = {
    title: "Foo",
    onChange: () => { },
    onRequestClose: () => { },
    initialValue: "",
};
export const Standard = {
    render: () => _jsx(ShareJsonModal, { ...sharedProps }),
    parameters: { colorScheme: "dark" },
};
export const StandardLight = {
    render: () => _jsx(ShareJsonModal, { ...sharedProps }),
    parameters: { colorScheme: "light" },
};
export const JSON = {
    render: () => _jsx(ShareJsonModal, { ...sharedProps, initialValue: { foo: "bar", baz: "qux" } }),
    parameters: { colorScheme: "dark" },
};
export const SubmittingInvalidLayout = {
    render: () => _jsx(ShareJsonModal, { ...sharedProps }),
    parameters: { colorScheme: "dark" },
    play: async () => {
        const textarea = await screen.findByTestId("share-json-input");
        fireEvent.change(textarea, { target: { value: "{" } });
    },
};
