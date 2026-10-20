import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
//
// This file incorporates work covered by the following copyright and
// permission notice:
//
//   Copyright 2019-2021 Cruise LLC
//
//   This source code is licensed under the Apache License, Version 2.0,
//   found at http://www.apache.org/licenses/LICENSE-2.0
//   You may not use this file except in compliance with the License.
import { Slider, Typography, useTheme } from "@mui/material";
import { useCallback, useState } from "react";
import { useDebouncedCallback } from "use-debounce";
import Panel from "@foxglove/studio-base/components/Panel";
import PanelToolbar from "@foxglove/studio-base/components/PanelToolbar";
import Stack from "@foxglove/studio-base/components/Stack";
import useGlobalVariables from "@foxglove/studio-base/hooks/useGlobalVariables";
import { useVariableSliderSettings } from "./settings";
function VariableSliderPanel(props) {
    const { config, saveConfig } = props;
    const { sliderProps, globalVariableName } = config;
    const { globalVariables, setGlobalVariables } = useGlobalVariables();
    const { min = 0, max = 10, step = 1 } = sliderProps;
    const globalVariableValue = globalVariables[globalVariableName];
    const theme = useTheme();
    const [sliderValue, setSliderValue] = useState(typeof globalVariableValue === "number" ? globalVariableValue : 0);
    useVariableSliderSettings(config, saveConfig);
    const updateVariable = useCallback((value) => {
        if (value !== globalVariableValue) {
            setGlobalVariables({ [globalVariableName]: value });
        }
    }, [globalVariableName, globalVariableValue, setGlobalVariables]);
    const updateVariableDebounced = useDebouncedCallback(updateVariable, 250);
    const sliderOnChange = useCallback((_event, value) => {
        setSliderValue(value);
        updateVariableDebounced(value);
    }, [setSliderValue, updateVariableDebounced]);
    const marks = [
        { value: min, label: String(min) },
        { value: max, label: String(max) },
    ];
    return (_jsxs(Stack, { fullHeight: true, children: [_jsx(PanelToolbar, {}), _jsxs(Stack, { flex: "auto", alignItems: "center", justifyContent: "center", fullHeight: true, gap: 2, paddingY: 2, paddingX: 3, children: [_jsx(Slider, { min: min, max: max, step: step, marks: marks, value: sliderValue, onChange: sliderOnChange }), _jsx(Typography, { variant: "h5", style: { marginTop: theme.spacing(-2.5) }, children: sliderValue })] })] }));
}
const defaultConfig = {
    sliderProps: {
        min: 0,
        max: 10,
        step: 1,
    },
    globalVariableName: "globalVariable",
};
export default Panel(Object.assign(VariableSliderPanel, {
    panelType: "GlobalVariableSliderPanel",
    defaultConfig,
}));
