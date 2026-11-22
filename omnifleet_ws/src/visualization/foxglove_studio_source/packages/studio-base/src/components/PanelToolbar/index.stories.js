import { jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
//
// This file incorporates work covered by the following copyright and
// permission notice:
//
//   Copyright 2018-2021 Cruise LLC
//
//   This source code is licensed under the Apache License, Version 2.0,
//   found at http://www.apache.org/licenses/LICENSE-2.0
//   You may not use this file except in compliance with the License.
import { Database20Filled } from "@fluentui/react-icons";
import { useTheme } from "@mui/material";
import { fireEvent, screen } from "@storybook/testing-library";
import { Mosaic, MosaicWindow } from "react-mosaic-component";
import MockPanelContextProvider from "@foxglove/studio-base/components/MockPanelContextProvider";
import ToolbarIconButton from "@foxglove/studio-base/components/PanelToolbar/ToolbarIconButton";
import MockCurrentLayoutProvider from "@foxglove/studio-base/providers/CurrentLayoutProvider/MockCurrentLayoutProvider";
import { PanelStateContextProvider } from "@foxglove/studio-base/providers/PanelStateContextProvider";
import WorkspaceContextProvider from "@foxglove/studio-base/providers/WorkspaceContextProvider";
import PanelToolbar from "./index";
import "react-mosaic-component/react-mosaic-component.css";
function MosaicWrapper(props) {
    const { children, layout = "dummy", width = 268 } = props;
    const theme = useTheme();
    return (_jsx(WorkspaceContextProvider, { children: _jsx(Mosaic, { onChange: () => undefined, renderTile: (id, path) => (_jsx(MosaicWindow, { title: "test", path: path, toolbarControls: _jsx("div", {}), renderPreview: () => undefined, children: _jsx(PanelStateContextProvider, { children: _jsx("div", { style: {
                            width: "100%",
                            height: "100%",
                            padding: theme.spacing(3),
                            position: "relative",
                            backgroundColor: theme.palette.background.default,
                        }, children: _jsx("div", { style: { width }, children: id === "Sibling" ? "Sibling Panel" : children }) }) }) })), value: layout, className: "mosaic-foxglove-theme" // prevent the default mosaic theme from being applied
         }) }));
}
export default {
    title: "components/PanelToolbar",
    decorators: [
        (Story) => {
            // Provide all stories with PanelContext and current layout
            return (_jsx(MockCurrentLayoutProvider, { children: _jsx(MockPanelContextProvider, { children: _jsx(Story, {}) }) }));
        },
    ],
};
const ToolbarContent = () => (_jsx("div", { style: { width: "100%", lineHeight: "22px", paddingLeft: 5 }, children: "Some controls here" }));
export const NonFloatingNarrow = {
    render: () => {
        return (_jsx(MosaicWrapper, { children: _jsx(PanelToolbar, { children: _jsx(ToolbarContent, {}) }) }));
    },
    name: "non-floating (narrow)",
};
export const NonFloatingWideWithPanelName = {
    render: (args) => {
        return (_jsx(MosaicWrapper, { ...args, children: _jsx(PanelToolbar, { children: _jsx(ToolbarContent, {}) }) }));
    },
    args: { width: 468 },
    name: "non-floating (wide with panel name)",
};
export const OneAdditionalIcon = {
    render: (args) => {
        const additionalIcons = (_jsx(ToolbarIconButton, { title: "database icon", children: _jsx(Database20Filled, {}) }));
        return (_jsx(MosaicWrapper, { ...args, children: _jsx(PanelToolbar, { additionalIcons: additionalIcons, children: _jsx(ToolbarContent, {}) }) }));
    },
    args: { width: 468 },
    name: "one additional icon",
};
export const MenuOnlyPanel = {
    render: () => (_jsx(MosaicWrapper, { children: _jsx(PanelToolbar, { children: _jsx(ToolbarContent, {}) }) })),
    name: "menu (only panel)",
    parameters: { colorScheme: "dark" },
    play: async () => {
        fireEvent.click(await screen.findByTestId("panel-menu"));
    },
};
export const MenuLight = {
    render: () => (_jsx(MosaicWrapper, { children: _jsx(PanelToolbar, { children: _jsx(ToolbarContent, {}) }) })),
    name: "menu light",
    parameters: { colorScheme: "light" },
    play: async () => {
        fireEvent.click(await screen.findByTestId("panel-menu"));
    },
};
export const MenuWithSiblingPanel = {
    render: (args) => (_jsx(MosaicWrapper, { ...args, children: _jsx(PanelToolbar, { children: _jsx(ToolbarContent, {}) }) })),
    name: "menu (with sibling panel)",
    args: { layout: { direction: "row", first: "dummy", second: "Sibling" } },
    parameters: { colorScheme: "dark" },
    play: async () => {
        fireEvent.click(await screen.findByTestId("panel-menu"));
    },
};
export const MenuForTabPanel = {
    render: (args) => (_jsx(MosaicWrapper, { ...args, children: _jsx(PanelToolbar, { children: _jsx(ToolbarContent, {}) }) })),
    name: "menu for Tab panel",
    args: { layout: { direction: "row", first: "Tab", second: "Sibling" } },
    parameters: { colorScheme: "dark" },
    play: async () => {
        fireEvent.click(await screen.findByTestId("panel-menu"));
    },
};
export const NoToolbars = {
    render: (args) => (_jsx(MosaicWrapper, { ...args, children: _jsx(PanelToolbar, { children: _jsx(ToolbarContent, {}) }) })),
    args: { layout: { direction: "row", first: "dummy", second: "Sibling" } },
    name: "no toolbars",
    parameters: { colorScheme: "dark" },
    play: async () => {
        fireEvent.click(await screen.findByTestId("panel-menu"));
    },
};
export const Chinese = {
    ...MenuLight,
    name: undefined,
    parameters: { forceLanguage: "zh", colorScheme: "light" },
};
export const Japanese = {
    ...MenuLight,
    name: undefined,
    parameters: { forceLanguage: "ja", colorScheme: "light" },
};
