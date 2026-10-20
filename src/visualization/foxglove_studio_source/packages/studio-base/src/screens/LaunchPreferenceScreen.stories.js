import { jsx as _jsx } from "react/jsx-runtime";
import { LaunchPreferenceScreen } from "@foxglove/studio-base/screens/LaunchPreferenceScreen";
export default {
    title: "LaunchPreferenceScreen",
    component: LaunchPreferenceScreen,
};
export const Dark = {
    render: () => {
        return _jsx(LaunchPreferenceScreen, {});
    },
    parameters: { colorScheme: "dark" },
};
export const Light = {
    render: () => {
        return _jsx(LaunchPreferenceScreen, {});
    },
    parameters: { colorScheme: "light" },
};
