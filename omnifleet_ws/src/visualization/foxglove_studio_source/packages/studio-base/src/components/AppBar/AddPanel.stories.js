import { jsx as _jsx, Fragment as _Fragment } from "react/jsx-runtime";
import { AddPanelMenu } from "./AddPanelMenu";
import { StorybookDecorator } from "./StorybookDecorator.stories";
export default {
    title: "components/AppBar/AddPanelMenu",
    component: AddPanelMenu,
    decorators: [StorybookDecorator],
};
export const Default = {
    render: () => {
        return (_jsx(_Fragment, { children: _jsx(AddPanelMenu, { open: true, anchorReference: "anchorPosition", anchorPosition: { left: 0, top: 0 }, disablePortal: true, handleClose: () => {
                    // no-op
                } }) }));
    },
};
