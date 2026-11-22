import { jsx as _jsx } from "react/jsx-runtime";
import { screen, userEvent } from "@storybook/testing-library";
import { useState } from "react";
import { ColorPickerControl, useColorPickerControl } from "./ColorPickerControl";
export default {
    title: "components/ColorPickerControl",
    component: ColorPickerControl,
};
export const Default = {
    render: function Story() {
        const [color, setColor] = useState("#ffaa00");
        const colorPickerProps = useColorPickerControl({
            alphaType: "none",
            onChange: setColor,
            value: color,
        });
        return _jsx(ColorPickerControl, { ...colorPickerProps });
    },
};
export const WithAlpha = {
    render: function Story() {
        const [color, setColor] = useState("#ffaa0088");
        const colorPickerProps = useColorPickerControl({
            alphaType: "alpha",
            onChange: setColor,
            value: color,
        });
        return _jsx(ColorPickerControl, { ...colorPickerProps });
    },
};
export const TextEntry = {
    render: function Story() {
        const [color, setColor] = useState("");
        const colorPickerProps = useColorPickerControl({
            alphaType: "none",
            onChange: setColor,
            value: color,
        });
        return _jsx(ColorPickerControl, { ...colorPickerProps });
    },
    play: async () => {
        const { click, type } = userEvent.setup();
        const inputs = await screen.findAllByPlaceholderText("RRGGBB");
        for (const input of inputs) {
            await click(input);
            await type(input, "aabbcc");
        }
    },
};
