import { jsx as _jsx } from "react/jsx-runtime";
import { useHoverValue } from "@foxglove/studio-base/context/TimelineInteractionStateContext";
import { VerticalBarWrapper } from "./VerticalBarWrapper";
export default React.memo(function HoverBar({ children, componentId, isPlaybackSeconds, scales, }) {
    const hoverValue = useHoverValue({ componentId, isPlaybackSeconds });
    return (_jsx(VerticalBarWrapper, { scales: scales, xValue: hoverValue?.value, children: children }));
});
