import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { useCallback } from "react";
import Stack from "@foxglove/studio-base/components/Stack";
import { NumberInput } from "./NumberInput";
export function Vec3Input(props) {
    const { disabled = false, onChange, precision, readOnly = false, step, value, min, max, placeholder, } = props;
    const onChangeCallback = useCallback((position, inputValue) => {
        const newValue = [
            ...(value ?? [0, 0, 0]),
        ];
        newValue[position] = inputValue;
        onChange(newValue);
    }, [onChange, value]);
    return (_jsxs(Stack, { gap: 0.25, children: [_jsx(NumberInput, { size: "small", disabled: disabled, readOnly: readOnly, variant: "filled", fullWidth: true, precision: precision, step: step, placeholder: placeholder?.[0], value: value?.[0], min: min, max: max, onChange: (newValue) => {
                    onChangeCallback(0, newValue);
                } }), _jsx(NumberInput, { size: "small", disabled: disabled, readOnly: readOnly, variant: "filled", fullWidth: true, precision: precision, step: step, placeholder: placeholder?.[1], value: value?.[1], min: min, max: max, onChange: (newValue) => {
                    onChangeCallback(1, newValue);
                } }), _jsx(NumberInput, { size: "small", disabled: disabled, readOnly: readOnly, variant: "filled", fullWidth: true, precision: precision, step: step, placeholder: placeholder?.[2], value: value?.[2], min: min, max: max, onChange: (newValue) => {
                    onChangeCallback(2, newValue);
                } })] }));
}
