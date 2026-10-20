import { jsx as _jsx } from "react/jsx-runtime";
export function ExpectedResult(props) {
    const { children, top = 25, left = 0 } = props;
    return (_jsx("div", { style: { position: "fixed", top, left, color: "lightgreen", margin: 16, zIndex: 1000 }, children: children }));
}
