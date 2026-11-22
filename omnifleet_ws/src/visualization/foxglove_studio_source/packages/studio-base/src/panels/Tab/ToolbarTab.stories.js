import { jsx as _jsx } from "react/jsx-runtime";
import * as _ from "lodash-es";
import React from "react";
import { ToolbarTab } from "@foxglove/studio-base/panels/Tab/ToolbarTab";
const baseProps = {
    hidden: false,
    highlight: undefined,
    innerRef: undefined,
    isActive: false,
    isDragging: false,
    actions: {
        addTab: _.noop,
        removeTab: _.noop,
        selectTab: _.noop,
        setTabTitle: _.noop,
    },
    tabCount: 1,
    tabIndex: 0,
    tabTitle: "Tab Title",
};
const Container = React.forwardRef(function Container({ children }, ref) {
    return (_jsx("div", { style: { margin: 8 }, ref: ref, children: children }));
});
export default {
    title: "panels/Tab/ToolbarTab",
};
export const Default = {
    render: () => (_jsx(Container, { children: _jsx(ToolbarTab, { ...baseProps }) })),
    name: "default",
};
export const ActiveWithCloseIcon = {
    render: () => (_jsx(Container, { children: _jsx(ToolbarTab, { ...baseProps, isActive: true, tabCount: 3 }) })),
    name: "active with close icon",
};
export const ActiveWithoutCloseIcon = {
    render: () => (_jsx(Container, { children: _jsx(ToolbarTab, { ...baseProps, isActive: true, tabCount: 1 }) })),
    name: "active without close icon",
};
export const Hidden = {
    render: () => (_jsx(Container, { children: _jsx(ToolbarTab, { ...baseProps, hidden: true }) })),
    name: "hidden",
};
export const Highlight = {
    render: () => (_jsx(Container, { children: _jsx(ToolbarTab, { ...baseProps, highlight: "before" }) })),
    name: "highlight",
};
export const Dragging = {
    render: () => (_jsx(Container, { children: _jsx(ToolbarTab, { ...baseProps, isDragging: true }) })),
    name: "dragging",
};
export const Editing = {
    render: () => (_jsx(Container, { children: _jsx(ToolbarTab, { ...baseProps, isActive: true }) })),
    name: "editing",
    play: () => {
        document.querySelectorAll("input")[0].click();
    },
};
