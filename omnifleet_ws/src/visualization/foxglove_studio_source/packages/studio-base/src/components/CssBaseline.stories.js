import { jsx as _jsx } from "react/jsx-runtime";
import CssBaseline from "./CssBaseline";
export default {
    component: CssBaseline,
    title: "components/CssBaseline",
    parameters: {
        colorScheme: "light",
    },
};
export const Scrollbars = {
    render: () => {
        return (_jsx(CssBaseline, { children: _jsx("div", { style: { width: "200px", height: "200px", border: "1px solid black", overflow: "scroll" }, children: _jsx("div", { style: { width: "400px", height: "400px" }, children: "Should have both scrollbars" }) }) }));
    },
};
