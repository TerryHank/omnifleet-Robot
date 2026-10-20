import { jsx as _jsx } from "react/jsx-runtime";
import PlayerSelectionContext from "@foxglove/studio-base/context/PlayerSelectionContext";
import MockCurrentLayoutProvider from "@foxglove/studio-base/providers/CurrentLayoutProvider/MockCurrentLayoutProvider";
import WorkspaceContextProvider from "@foxglove/studio-base/providers/WorkspaceContextProvider";
import { DataSourceDialog } from "./DataSourceDialog";
const Wrapper = (Story) => {
    return (_jsx(MockCurrentLayoutProvider, { children: _jsx(WorkspaceContextProvider, { initialState: {
                dialogs: {
                    dataSource: {
                        activeDataSource: undefined,
                        item: "connection",
                        open: true,
                    },
                    preferences: {
                        initialTab: undefined,
                        open: false,
                    },
                },
            }, children: _jsx(PlayerSelectionContext.Provider, { value: playerSelection, children: _jsx(Story, {}) }) }) }));
};
export default {
    title: "components/DataSourceDialog/Connection",
    component: DataSourceDialog,
    decorators: [Wrapper],
};
// Connection
const playerSelection = {
    selectSource: () => { },
    selectRecent: () => { },
    recentSources: [],
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
        {
            id: "bar",
            type: "connection",
            displayName: "Another data source",
            description: "Another description (with default icon)",
            initialize: () => {
                return undefined;
            },
        },
        {
            id: "bar",
            type: "connection",
            displayName: "Another data source",
            description: "Another description (with default icon)",
            iconName: "GenericScan",
            initialize: () => {
                return undefined;
            },
        },
    ],
};
export const Light = {
    render: () => _jsx(DataSourceDialog, { backdropAnimation: false }),
    name: "Default (light)",
    parameters: { colorScheme: "light" },
};
export const LightChinese = {
    ...Light,
    name: "Default Chinese",
    parameters: { forceLanguage: "zh", colorScheme: "light" },
};
export const LightJapanese = {
    ...Light,
    name: "Default Japanese",
    parameters: { forceLanguage: "ja", colorScheme: "light" },
};
export const Dark = {
    render: () => _jsx(DataSourceDialog, { backdropAnimation: false }),
    name: "Default (dark)",
    parameters: { colorScheme: "dark" },
};
