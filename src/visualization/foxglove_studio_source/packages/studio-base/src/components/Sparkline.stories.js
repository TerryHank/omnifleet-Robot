import { jsx as _jsx } from "react/jsx-runtime";
import { Sparkline } from "@foxglove/studio-base/components/Sparkline";
const points = [
    { value: 5, timestamp: 10 },
    { value: 50, timestamp: 30 },
    { value: 30, timestamp: 60 },
    { value: 100, timestamp: 100 },
];
const props = {
    points,
    width: 300,
    height: 100,
    timeRange: 100,
    nowStamp: 100,
};
export default {
    title: "components/Sparkline",
};
export const Standard = {
    render: () => {
        return (_jsx("div", { style: { padding: 8 }, children: _jsx(Sparkline, { ...props }) }));
    },
    name: "standard",
};
export const WithExplicitMaximumOf200 = {
    render: () => {
        return (_jsx("div", { style: { padding: 8 }, children: _jsx(Sparkline, { ...props, maximum: 200 }) }));
    },
    name: "with explicit maximum of 200",
};
