import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { fireEvent, screen } from "@storybook/testing-library";
import TextMiddleTruncate from "./TextMiddleTruncate";
const LONG_TOPIC_NAME = "/some_really_long_topic_name/some/long/text/lorem/ipsum/dolor/sit/amet/consectetur/adipisicing/voluptate/laborum/amet/velit/eius/cum/modi//sapiente/natus/unde/end_topic_name";
export default {
    title: "components/TextMiddleTruncate",
    component: TextMiddleTruncate,
};
async function hoverText() {
    const allText = await screen.findAllByTestId("text-middle-truncate");
    fireEvent.pointerOver(allText[3]);
}
export const Default = {
    render: function Story() {
        return (_jsxs("div", { style: {
                display: "grid",
                gridAutoRows: 84,
                gridTemplateColumns: "300px 240px",
                gap: 16,
                padding: 16,
            }, children: [_jsx("div", { children: "Short text:" }), _jsx(TextMiddleTruncate, { text: "Some short text" }), _jsx("div", { children: "Long text:" }), _jsx(TextMiddleTruncate, { text: "Some long text Lorem ipsum dolor sit amet consectetur adipisicing elit. Voluptate laborum amet velit eius cum modi qui. Sapiente natus unde assumenda." }), _jsx("div", { children: "Specifify endTextLength as 20:" }), _jsx(TextMiddleTruncate, { endTextLength: 20, text: "Some long text Lorem ipsum dolor sit amet consectetur adipisicing elit. Voluptate laborum amet velit eius cum modi qui. Sapiente natus unde assumenda." }), _jsx("div", { children: "Show the last part of topic name with visibile text:" }), _jsx(TextMiddleTruncate, { endTextLength: LONG_TOPIC_NAME.split("/").pop().length + 1, text: LONG_TOPIC_NAME }), _jsx("div", { children: "Whitespace handling" }), _jsx("div", { style: { width: "12em" }, children: _jsx(TextMiddleTruncate, { text: "Open a new connection\u2026", endTextLength: 18 }) })] }));
    },
    play: hoverText,
};
