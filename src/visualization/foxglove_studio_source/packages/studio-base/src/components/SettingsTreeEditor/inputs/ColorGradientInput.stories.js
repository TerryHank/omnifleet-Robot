import { jsx as _jsx } from "react/jsx-runtime";
import { useState } from "react";
import { ColorGradientInput } from "./ColorGradientInput";
export default {
    title: "components/ColorGradientInput",
    component: ColorGradientInput,
};
export const Default = {
    render: function Story() {
        const [colors, setColors] = useState(["#ffaa00", "#0026ff"]);
        return _jsx(ColorGradientInput, { colors: colors, onChange: setColors });
    },
};
export const Disabled = {
    render: function Story() {
        const [colors, setColors] = useState(["#ffaa00", "#0026ff"]);
        return _jsx(ColorGradientInput, { disabled: true, colors: colors, onChange: setColors });
    },
};
export const ReadOnly = {
    render: function Story() {
        const [colors, setColors] = useState(["#ffaa00", "#0026ff"]);
        return _jsx(ColorGradientInput, { readOnly: true, colors: colors, onChange: setColors });
    },
};
export const WithAlpha = {
    render: function Story() {
        const [colors, setColors] = useState(["#ffaa0088", "#0026ffcc"]);
        return _jsx(ColorGradientInput, { colors: colors, onChange: setColors });
    },
};
