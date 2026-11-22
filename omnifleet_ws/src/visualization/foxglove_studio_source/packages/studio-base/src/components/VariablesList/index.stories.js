import { jsx as _jsx } from "react/jsx-runtime";
import { fireEvent, screen } from "@storybook/testing-library";
import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import MockCurrentLayoutProvider from "@foxglove/studio-base/providers/CurrentLayoutProvider/MockCurrentLayoutProvider";
import VariablesList from ".";
export default {
    title: "components/VariablesList",
    component: VariablesList,
};
const initialState = {
    globalVariables: {
        selected_id: 1234,
    },
};
const bigVariableInitialState = {
    globalVariables: {
        big: {
            cameraState: {
                distance: 20,
                perspective: true,
                phi: 60,
                target: [0, 0, 0],
                targetOffset: [0, 0, 0],
                targetOrientation: [0, 0, 0, 1],
                thetaOffset: 45,
                fovy: 45,
                near: 0.5,
                far: 5000,
            },
        },
    },
};
export const Default = {
    render: () => {
        return (_jsx(DndProvider, { backend: HTML5Backend, children: _jsx(MockCurrentLayoutProvider, { children: _jsx(VariablesList, {}) }) }));
    },
};
export const Interactive = {
    render: function Story() {
        return (_jsx(DndProvider, { backend: HTML5Backend, children: _jsx(MockCurrentLayoutProvider, { children: _jsx(VariablesList, {}) }) }));
    },
    play: async () => {
        const addButton = await screen.findByTestId("add-variable-button");
        fireEvent.click(addButton);
        const input = await screen.findByPlaceholderText("variable_name");
        fireEvent.change(input, { target: { value: "new_variable_name" } });
        const valueInput = await screen.findByDisplayValue('""');
        fireEvent.change(valueInput, { target: { value: '"edited value"' } });
        const menuButton = await screen.findByTestId("variable-action-button");
        fireEvent.click(menuButton);
        await screen.findByTestId("global-variable-key-input-new_variable_name");
        const menuButton2 = await screen.findByTestId("variable-action-button");
        fireEvent.click(menuButton2);
        const deleteButton = await screen.findByText("Delete variable");
        fireEvent.click(deleteButton);
    },
    parameters: { colorScheme: "light" },
};
export const WithBigVariable = {
    render: function Story() {
        return (_jsx(DndProvider, { backend: HTML5Backend, children: _jsx(MockCurrentLayoutProvider, { initialState: bigVariableInitialState, children: _jsx(VariablesList, {}) }) }));
    },
    parameters: { colorScheme: "light" },
};
export const WithVariablesLight = {
    render: function Story() {
        return (_jsx(DndProvider, { backend: HTML5Backend, children: _jsx(MockCurrentLayoutProvider, { initialState: initialState, children: _jsx(VariablesList, {}) }) }));
    },
    parameters: { colorScheme: "light" },
};
export const WithVariablesDark = {
    render: function Story() {
        return (_jsx(DndProvider, { backend: HTML5Backend, children: _jsx(MockCurrentLayoutProvider, { initialState: initialState, children: _jsx(VariablesList, {}) }) }));
    },
    parameters: { colorScheme: "dark" },
};
