import { jsx as _jsx } from "react/jsx-runtime";
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
    title: "components/DataSourceDialog",
    component: DataSourceDialog,
    decorators: [Wrapper],
};
export const DefaultLight = {
    render: () => _jsx(DataSourceDialog, {}),
    parameters: { colorScheme: "light" },
    name: "Default (light)",
};
export const DefaultDark = {
    render: () => _jsx(DataSourceDialog, {}),
    parameters: { colorScheme: "dark" },
    name: "Default (dark)",
};
