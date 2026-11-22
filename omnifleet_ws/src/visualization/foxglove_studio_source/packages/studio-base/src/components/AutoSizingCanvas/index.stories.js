import { jsx as _jsx } from "react/jsx-runtime";
import { useState, useEffect } from "react";
import AutoSizingCanvas from ".";
function Example({ changeSize = false, changePixelRatio = false, devicePixelRatio, }) {
    const [width, setWidth] = useState(300);
    const [pixelRatio, setPixelRatio] = useState(devicePixelRatio);
    useEffect(() => {
        const timeOutID = setTimeout(() => {
            if (changeSize) {
                setWidth(150);
            }
            if (changePixelRatio) {
                setPixelRatio(2);
            }
        }, 10);
        return () => {
            clearTimeout(timeOutID);
        };
    }, [changePixelRatio, changeSize]);
    return (_jsx("div", { style: { width, height: 100, backgroundColor: "green" }, children: _jsx(AutoSizingCanvas, { overrideDevicePixelRatioForTest: pixelRatio, draw: (ctx, drawWidth, drawHeight) => {
                ctx.fillStyle = "white";
                ctx.fillRect(0, 0, drawWidth, drawHeight);
                ctx.strokeStyle = "red";
                ctx.lineWidth = 2;
                ctx.font = "24px Arial";
                ctx.strokeRect(0, 0, drawWidth, drawHeight);
                const text = `hello ${ctx.getTransform().a}`;
                const size = ctx.measureText(text);
                ctx.fillStyle = "black";
                ctx.textBaseline = "middle";
                ctx.fillText(text, drawWidth / 2 - size.width / 2, drawHeight / 2);
            } }) }));
}
export default {
    title: "components/AutoSizingCanvas",
};
export const Static = {
    render: () => _jsx(Example, {}),
    name: "static",
};
export const ChangingSize = {
    render: () => _jsx(Example, { changeSize: true }),
    name: "changing size",
};
export const PixelRatio2 = {
    render: () => _jsx(Example, { devicePixelRatio: 2 }),
    name: "pixel ratio 2",
};
export const ChangingPixelRatio = {
    render: () => _jsx(Example, { changePixelRatio: true }),
    name: "changing pixel ratio",
};
