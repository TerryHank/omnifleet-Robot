import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { FormHelperText, TextField } from "@mui/material";
import { useState } from "react";
export function FormField(props) {
    const [error, setError] = useState();
    const field = props.field;
    const onChange = (event) => {
        setError(undefined);
        const maybeError = field.validate?.(event.target.value);
        if (maybeError instanceof Error) {
            setError(maybeError.message);
            props.onError(maybeError.message);
            return;
        }
        props.onChange(event.target.value);
    };
    return (_jsxs("div", { children: [_jsx(TextField, { fullWidth: true, disabled: props.disabled, label: field.label, error: error != undefined, helperText: error, FormHelperTextProps: {
                    variant: "standard",
                }, placeholder: field.placeholder, defaultValue: field.defaultValue, onChange: onChange, variant: "outlined", InputProps: {
                    notched: false,
                }, InputLabelProps: { shrink: true } }, field.label), _jsx(FormHelperText, { children: field.description })] }));
}
