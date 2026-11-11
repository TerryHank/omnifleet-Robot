import { jsx as _jsx } from "react/jsx-runtime";
import { useState } from "react";
import { PlayerCapabilities } from "@foxglove/studio-base/players/types";
import PanelSetup from "@foxglove/studio-base/stories/PanelSetup";
import Parameters from "./index";
const DEFAULT_PARAMS = new Map([
    ["undefined", undefined],
    ["boolean", false],
    ["number", -42],
    ["string", "Hello, world!"],
    ["date", new Date(1618876820517)],
    ["Uint8Array", new Uint8Array([0, 1])],
    ["array", [1, 2]],
    ["string array", ["one", "two", "three"]],
    ["struct", { a: 1, b: [2, 3], c: "String value" }],
]);
const getFixture = ({ getParameters, setParameters, parameters, setParameterValues, }) => {
    const capabilities = [];
    if (getParameters) {
        capabilities.push(PlayerCapabilities.getParameters);
    }
    if (setParameters) {
        capabilities.push(PlayerCapabilities.setParameters);
    }
    return {
        topics: [],
        frame: {},
        capabilities,
        activeData: {
            parameters: getParameters ? parameters : undefined,
        },
        setParameter: setParameters && setParameterValues
            ? (key, value) => {
                const params = new Map(parameters);
                params.set(key, value);
                setParameterValues(params);
            }
            : undefined,
    };
};
export default {
    title: "panels/Parameters",
    component: Parameters,
};
export const Default = {
    render: () => {
        return (_jsx(PanelSetup, { fixture: getFixture({ getParameters: false, setParameters: false }), children: _jsx(Parameters, {}) }));
    },
};
export const WithParameters = {
    render: () => {
        return (_jsx(PanelSetup, { fixture: getFixture({
                getParameters: true,
                setParameters: false,
                parameters: DEFAULT_PARAMS,
            }), children: _jsx(Parameters, {}) }));
    },
};
const EditableParameters = () => {
    const [parameters, setParameterValues] = useState(DEFAULT_PARAMS);
    return (_jsx(PanelSetup, { fixture: getFixture({
            getParameters: true,
            setParameters: true,
            parameters,
            setParameterValues,
        }), children: _jsx(Parameters, {}) }));
};
export const WithEditableParameters = {
    render: () => _jsx(EditableParameters, {}),
};
