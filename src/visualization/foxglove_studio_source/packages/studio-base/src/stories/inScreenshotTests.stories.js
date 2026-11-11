import { jsxs as _jsxs } from "react/jsx-runtime";
import inScreenshotTests from "@foxglove/studio-base/stories/inScreenshotTests";
export default {
    title: "inScreenshotTests",
};
export const InScreenshotTests = {
    render: () => {
        return (_jsxs("div", { style: {
                padding: "20px",
                fontSize: "20px",
                color: "white",
                backgroundColor: inScreenshotTests() ? "green" : "maroon",
            }, children: ["inScreenshotTests: ", JSON.stringify(inScreenshotTests())] }));
    },
};
