import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { action } from "@storybook/addon-actions";
import MockMessagePipelineProvider from "@foxglove/studio-base/components/MessagePipeline/MockMessagePipelineProvider";
import Stack from "@foxglove/studio-base/components/Stack";
import { PlayerPresence } from "@foxglove/studio-base/players/types";
import { AppBar } from ".";
import { StorybookDecorator } from "./StorybookDecorator.stories";
export default {
    title: "components/AppBar",
    component: AppBar,
    decorators: [StorybookDecorator],
    args: {
        onMinimizeWindow: action("onMinimizeWindow"),
        onMaximizeWindow: action("onMaximizeWindow"),
        onUnmaximizeWindow: action("onUnmaximizeWindow"),
        onCloseWindow: action("onCloseWindow"),
    },
    parameters: { colorScheme: "both-column" },
};
export const Default = {};
export const DefaultChinese = { parameters: { forceLanguage: "zh" } };
export const DefaultJapanese = { parameters: { forceLanguage: "ja" } };
export const CustomWindowControls = {
    args: { showCustomWindowControls: true },
};
export const CustomWindowControlsMaximized = {
    args: { isMaximized: true, showCustomWindowControls: true },
};
export const CustomWindowControlsDragRegion = {
    args: { showCustomWindowControls: true, debugDragRegion: true },
};
const Grid = (Story) => (_jsx(Stack, { overflowY: "auto", children: _jsx("div", { style: { display: "grid", gridTemplateColumns: "max-content auto", alignItems: "center" }, children: _jsx(Story, {}) }) }));
const problems = [
    { severity: "error", message: "example error" },
    { severity: "warn", message: "example warn" },
];
export const PlayerStates = {
    decorators: [
        (Story) => {
            const playerStates = [
                ...[
                    PlayerPresence.NOT_PRESENT,
                    PlayerPresence.INITIALIZING,
                    PlayerPresence.RECONNECTING,
                    PlayerPresence.BUFFERING,
                    PlayerPresence.PRESENT,
                ].map((presence) => ({
                    name: "https://exampleurl:2002",
                    presence,
                })),
                {
                    name: "https://exampleurl:2002",
                    presence: PlayerPresence.ERROR,
                    problems,
                },
                {
                    label: "INITIALIZING + problems",
                    name: "https://exampleurl:2002",
                    presence: PlayerPresence.INITIALIZING,
                    problems,
                },
                {
                    label: "INITIALIZING + no name",
                    name: undefined,
                    presence: PlayerPresence.INITIALIZING,
                    problems,
                },
            ];
            return (_jsx(_Fragment, { children: playerStates.map((props) => (_jsxs(MockMessagePipelineProvider, { name: props.name, presence: props.presence, problems: props.problems, children: [_jsx("div", { style: { padding: 8 }, children: props.label ?? props.presence }), _jsx("div", { children: _jsx(Story, {}) })] }, props.presence))) }));
        },
        Grid,
    ],
    parameters: { colorScheme: "light" },
};
export const PlayerStatesChinese = {
    ...PlayerStates,
    parameters: { colorScheme: "light", forceLanguage: "zh" },
};
export const PlayerStatesJapanese = {
    ...PlayerStates,
    parameters: { colorScheme: "light", forceLanguage: "ja" },
};
const fileSources = [
    "mcap-local-file",
    "ros1-local-bagfile",
    "ros2-local-bagfile",
    "ulog-local-file",
    "remote-file",
].map((sourceId) => ({
    name: "longexampleurlwith_specialcharaters-and-portnumber.ext",
    urlState: { sourceId },
}));
const remoteSources = [
    "rosbridge-websocket",
    "foxglove-websocket",
    "some other source type",
].map((sourceId) => ({
    name: "https://longexampleurlwith_specialcharaters-and-portnumber:3030",
    urlState: { sourceId },
}));
export const DataSources = {
    decorators: [
        (Story) => {
            const playerStates = [
                {
                    name: "Adapted from nuScenes dataset. Copyright © 2020 nuScenes. https://www.nuscenes.org/terms-of-use",
                    urlState: { sourceId: "sample-nuscenes" },
                },
                ...fileSources,
                ...remoteSources,
                {
                    label: "with problems",
                    name: "https://longexampleurlwith_error-and-portnumber:3030",
                    problems,
                },
            ];
            return (_jsx(_Fragment, { children: playerStates.map((props) => (_jsxs(MockMessagePipelineProvider, { name: props.name, presence: PlayerPresence.PRESENT, urlState: props.urlState, problems: props.problems, seekPlayback: () => { }, children: [_jsx("div", { style: { padding: 8 }, children: props.label ?? props.urlState?.sourceId }), _jsx("div", { children: _jsx(Story, {}) })] }, props.urlState?.sourceId))) }));
        },
        Grid,
    ],
    parameters: { colorScheme: "light" },
};
export const DataSourcesChinese = {
    ...DataSources,
    parameters: { colorScheme: "light", forceLanguage: "zh" },
};
export const DataSourcesJapanese = {
    ...DataSources,
    parameters: { colorScheme: "light", forceLanguage: "ja" },
};
