import { jsx as _jsx } from "react/jsx-runtime";
import { userEvent, within } from "@storybook/testing-library";
import * as _ from "lodash-es";
import PlayerSelectionContext from "@foxglove/studio-base/context/PlayerSelectionContext";
import MockCurrentLayoutProvider from "@foxglove/studio-base/providers/CurrentLayoutProvider/MockCurrentLayoutProvider";
import WorkspaceContextProvider from "@foxglove/studio-base/providers/WorkspaceContextProvider";
import { AppMenu } from "./AppMenu";
export default {
    title: "components/AppBar/AppMenu",
    component: AppMenu,
    args: {
        open: true,
        anchorPosition: { top: 0, left: 0 },
        anchorReference: "anchorPosition",
        disablePortal: true,
        handleClose: _.noop,
    },
    decorators: [
        (Story, { args: { testId: _testId, ...args } }) => (_jsx(MockCurrentLayoutProvider, { children: _jsx(WorkspaceContextProvider, { children: _jsx(PlayerSelectionContext.Provider, { value: playerSelection, children: _jsx(Story, { ...args }) }) }) })),
    ],
    play: async ({ canvasElement, args }) => {
        if (!args.testId) {
            return;
        }
        const canvas = within(canvasElement);
        await userEvent.hover(await canvas.findByTestId(args.testId));
    },
};
// Connection
const playerSelection = {
    selectSource: () => { },
    selectRecent: () => { },
    recentSources: [
        // prettier-ignore
        { id: "1111", title: "NuScenes-v1.0-mini-scene-0655-reallllllllly-long-name-8829908290831091.bag", },
        { id: "2222", title: "http://localhost:11311", label: "ROS 1" },
        { id: "3333", title: "ws://localhost:9090/", label: "Rosbridge (ROS 1 & 2)" },
        { id: "4444", title: "ws://localhost:8765", label: "Foxglove WebSocket" },
        { id: "5555", title: "ws://1.2.3.4:8765", label: "Foxglove WebSocket" },
        { id: "6666", title: "THIS ITEM SHOULD BE HIDDEN IN STORYBOOKS", label: "!!!!!!!!!!!!" },
    ],
    availableSources: [],
};
export const Default = {};
export const FileMenuDark = {
    args: { testId: "app-menu-file" },
    parameters: { colorScheme: "dark" },
};
export const FileMenuDarkChinese = {
    args: { testId: "app-menu-file" },
    parameters: { colorScheme: "dark", forceLanguage: "zh" },
};
export const FileMenuDarkJapanese = {
    args: { testId: "app-menu-file" },
    parameters: { colorScheme: "dark", forceLanguage: "ja" },
};
export const FileMenuLight = {
    args: { testId: "app-menu-file" },
    parameters: { colorScheme: "light" },
};
export const FileMenuLightChinese = {
    args: { testId: "app-menu-file" },
    parameters: { colorScheme: "light", forceLanguage: "zh" },
};
export const FileMenuLightJapanese = {
    args: { testId: "app-menu-file" },
    parameters: { colorScheme: "light", forceLanguage: "ja" },
};
export const ViewMenuDark = {
    args: { testId: "app-menu-view" },
    parameters: { colorScheme: "dark" },
};
export const ViewMenuDarkChinese = {
    args: { testId: "app-menu-view" },
    parameters: { colorScheme: "dark", forceLanguage: "zh" },
};
export const ViewMenuDarkJapanese = {
    args: { testId: "app-menu-view" },
    parameters: { colorScheme: "dark", forceLanguage: "ja" },
};
export const ViewMenuLight = {
    args: { testId: "app-menu-view" },
    parameters: { colorScheme: "light" },
};
export const ViewMenuLightChinese = {
    args: { testId: "app-menu-view" },
    parameters: { colorScheme: "light", forceLanguage: "zh" },
};
export const ViewMenuLightJapanese = {
    ...ViewMenuLight,
    parameters: { colorScheme: "light", forceLanguage: "ja" },
};
export const HelpMenuDark = {
    args: { testId: "app-menu-help" },
    parameters: { colorScheme: "dark" },
};
export const HelpMenuDarkChinese = {
    args: { testId: "app-menu-help" },
    parameters: { colorScheme: "dark", forceLanguage: "zh" },
};
export const HelpMenuDarkJapanese = {
    args: { testId: "app-menu-help" },
    parameters: { colorScheme: "dark", forceLanguage: "ja" },
};
export const HelpMenuLight = {
    args: { testId: "app-menu-help" },
    parameters: { colorScheme: "light" },
};
export const HelpMenuLightChinese = {
    args: { testId: "app-menu-help" },
    parameters: { colorScheme: "light", forceLanguage: "zh" },
};
export const HelpMenuLightJapanese = {
    args: { testId: "app-menu-help" },
    parameters: { colorScheme: "light", forceLanguage: "ja" },
};
