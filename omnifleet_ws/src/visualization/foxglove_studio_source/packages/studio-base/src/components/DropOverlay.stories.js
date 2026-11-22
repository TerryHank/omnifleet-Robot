import { jsx as _jsx } from "react/jsx-runtime";
import DropOverlay from "@foxglove/studio-base/components/DropOverlay";
export default {
    title: "components/DropOverlay",
    component: DropOverlay,
};
export const Dark = {
    render: () => _jsx(DropOverlay, { open: true, children: "Some DropOverlay" }),
    parameters: { colorScheme: "dark" },
};
export const Light = {
    render: () => _jsx(DropOverlay, { open: true, children: "Some DropOverlay" }),
    parameters: { colorScheme: "light" },
};
