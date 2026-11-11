import { jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { action } from "@storybook/addon-actions";
import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import PanelErrorBoundary from "./PanelErrorBoundary";
function Broken() {
    throw Object.assign(new Error("Hello!"), {
        stack: `
  an error occurred
  it's caught by this component
  now the user sees
      `,
    });
    return ReactNull;
}
export default {
    title: "components/PanelErrorBoundary",
};
export const Default = {
    render: () => {
        return (_jsx(DndProvider, { backend: HTML5Backend, children: _jsx(PanelErrorBoundary, { onRemovePanel: action("onRemovePanel"), onResetPanel: action("onResetPanel"), children: _jsx(Broken, {}) }) }));
    },
};
export const ShowingDetails = {
    render: () => {
        return (_jsx(DndProvider, { backend: HTML5Backend, children: _jsx(PanelErrorBoundary, { showErrorDetails: true, hideErrorSourceLocations: true, onRemovePanel: action("onRemovePanel"), onResetPanel: action("onResetPanel"), children: _jsx(Broken, {}) }) }));
    },
};
