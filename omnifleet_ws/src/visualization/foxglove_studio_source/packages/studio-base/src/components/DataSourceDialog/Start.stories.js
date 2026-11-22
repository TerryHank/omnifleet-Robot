import { jsx as _jsx } from "react/jsx-runtime";
import BaseUserContext from "@foxglove/studio-base/context/BaseUserContext";
import PlayerSelectionContext from "@foxglove/studio-base/context/PlayerSelectionContext";
import MockCurrentLayoutProvider from "@foxglove/studio-base/providers/CurrentLayoutProvider/MockCurrentLayoutProvider";
import WorkspaceContextProvider from "@foxglove/studio-base/providers/WorkspaceContextProvider";
import { DataSourceDialog } from "./DataSourceDialog";
const Wrapper = (Story) => {
    return (_jsx(MockCurrentLayoutProvider, { children: _jsx(WorkspaceContextProvider, { initialState: {
                dialogs: {
                    dataSource: {
                        activeDataSource: undefined,
                        item: "start",
                        open: true,
                    },
                    preferences: {
                        initialTab: undefined,
                        open: false,
                    },
                },
            }, children: _jsx(Story, {}) }) }));
};
export default {
    title: "components/DataSourceDialog/Start",
    component: DataSourceDialog,
    parameters: { colorScheme: "dark" },
    decorators: [Wrapper],
};
// Connection
const playerSelection = {
    selectSource: () => { },
    selectRecent: () => { },
    recentSources: [
        {
            id: "1111",
            title: "NuScenes-v1.0-mini-scene-0655-reallllllllly-long-name-8829908290831091.bag",
        },
        {
            id: "2222",
            title: "http://localhost:11311",
            label: "ROS 1",
        },
        {
            id: "3333",
            title: "ws://localhost:9090/",
            label: "Rosbridge (ROS 1 & 2)",
        },
        {
            id: "4444",
            title: "ws://localhost:8765",
            label: "Foxglove WebSocket",
        },
        {
            id: "5555",
            title: "ws://1.2.3.4:8765",
            label: "Foxglove WebSocket",
        },
        {
            id: "6666",
            title: "THIS ITEM SHOULD BE HIDDEN IN STORYBOOKS",
            label: "!!!!!!!!!!!!",
        },
    ],
    availableSources: [
        {
            id: "foo",
            type: "connection",
            displayName: "My Data Source",
            description: "Data source description",
            iconName: "ROS",
            warning: "This is a warning",
            formConfig: {
                fields: [{ id: "key", label: "Some Label" }],
            },
            initialize: () => {
                return undefined;
            },
        },
    ],
};
function CurrentUserWrapper(props) {
    const value = {
        currentUserType: props.userType ?? "unauthenticated",
        signIn: () => undefined,
        signOut: async () => undefined,
    };
    return _jsx(BaseUserContext.Provider, { value: value, children: props.children });
}
const Default = () => _jsx(DataSourceDialog, { backdropAnimation: false });
export const DefaultLight = {
    render: Default,
    name: "Default (light)",
    parameters: { colorScheme: "light" },
};
export const DefaultDark = {
    render: Default,
    name: "Default (dark)",
    parameters: { colorScheme: "dark" },
};
export const UserNoAuth = {
    render: () => {
        return (_jsx(PlayerSelectionContext.Provider, { value: playerSelection, children: _jsx(DataSourceDialog, { backdropAnimation: false }) }));
    },
    name: "User not authenticated",
};
export const UserNoAuthChinese = {
    ...UserNoAuth,
    name: "User not authenticated Chinese",
    parameters: { forceLanguage: "zh" },
};
export const UserNoAuthJapanese = {
    ...UserNoAuth,
    name: "User not authenticated Japanese",
    parameters: { forceLanguage: "ja" },
};
export const UserPrivate = {
    render: () => {
        return (_jsx(CurrentUserWrapper, { children: _jsx(PlayerSelectionContext.Provider, { value: playerSelection, children: _jsx(DataSourceDialog, { backdropAnimation: false }) }) }));
    },
    name: "User not authenticated (private)",
};
export const UserPrivateChinese = {
    ...UserPrivate,
    name: "User not authenticated (private) Chinese",
    parameters: { forceLanguage: "zh" },
};
export const UserPrivateJapanese = {
    ...UserPrivate,
    name: "User not authenticated (private) Japanese",
    parameters: { forceLanguage: "ja" },
};
export const UserAuthedFree = {
    render: () => {
        return (_jsx(CurrentUserWrapper, { userType: "authenticated-free", children: _jsx(PlayerSelectionContext.Provider, { value: playerSelection, children: _jsx(DataSourceDialog, { backdropAnimation: false }) }) }));
    },
    name: "User Authenticated with Free Account",
};
export const UserAuthedFreeChinese = {
    ...UserAuthedFree,
    name: "User Authenticated with Free Account Chinese",
    parameters: { forceLanguage: "zh" },
};
export const UserAuthedFreeJapanese = {
    ...UserAuthedFree,
    name: "User Authenticated with Free Account Japanese",
    parameters: { forceLanguage: "ja" },
};
export const UserAuthedPaid = {
    render: () => {
        return (_jsx(CurrentUserWrapper, { userType: "authenticated-team", children: _jsx(PlayerSelectionContext.Provider, { value: playerSelection, children: _jsx(DataSourceDialog, { backdropAnimation: false }) }) }));
    },
    name: "User Authenticated with Paid Account",
};
export const UserAuthedPaidChinese = {
    ...UserAuthedPaid,
    name: "User Authenticated with Paid Account Chinese",
    parameters: { forceLanguage: "zh" },
};
export const UserAuthedPaidJapanese = {
    ...UserAuthedPaid,
    name: "User Authenticated with Paid Account Japanese",
    parameters: { forceLanguage: "ja" },
};
