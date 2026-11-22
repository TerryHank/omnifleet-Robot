import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import CancelIcon from "@mui/icons-material/Cancel";
import ErrorIcon from "@mui/icons-material/Error";
import { Autocomplete, MenuItem, MenuList, Select, TextField, ToggleButton, ToggleButtonGroup, Tooltip, Typography, } from "@mui/material";
import { makeStyles } from "tss-react/mui";
import { v4 as uuid } from "uuid";
import MessagePathInput from "@foxglove/studio-base/components/MessagePathSyntax/MessagePathInput";
import Stack from "@foxglove/studio-base/components/Stack";
import { useAppContext } from "@foxglove/studio-base/context/AppContext";
import { ColorGradientInput, ColorPickerInput, NumberInput, Vec2Input, Vec3Input } from "./inputs";
/** Used to allow both undefined and empty string in select inputs. */
const UNDEFINED_SENTINEL_VALUE = uuid();
/** Used to avoid MUI errors when an invalid option is selected */
const INVALID_SENTINEL_VALUE = uuid();
const useStyles = makeStyles()((theme, _params, classes) => ({
    autocomplete: {
        ".MuiInputBase-root.MuiInputBase-sizeSmall": {
            paddingInline: 0,
            paddingBlock: theme.spacing(0.3125),
        },
    },
    clearIndicator: {
        marginRight: theme.spacing(-0.25),
        opacity: theme.palette.action.disabledOpacity,
        ":hover": {
            background: "transparent",
            opacity: 1,
        },
    },
    error: {},
    fieldLabel: {
        color: theme.palette.text.secondary,
        overflow: "hidden",
        textOverflow: "ellipsis",
        whiteSpace: "nowrap",
    },
    fieldWrapper: {
        minWidth: theme.spacing(14),
        marginRight: theme.spacing(0.5),
        [`&.${classes.error} .MuiInputBase-root, .MuiInputBase-root.${classes.error}`]: {
            outline: `1px ${theme.palette.error.main} solid`,
            outlineOffset: -1,
        },
    },
    multiLabelWrapper: {
        display: "grid",
        gridTemplateColumns: "1fr auto",
        columnGap: theme.spacing(0.5),
        height: "100%",
        width: "100%",
        alignItems: "center",
        textAlign: "end",
    },
    styledToggleButtonGroup: {
        backgroundColor: theme.palette.action.hover,
        gap: theme.spacing(0.25),
        overflowX: "auto",
        "& .MuiToggleButtonGroup-grouped": {
            margin: theme.spacing(0.55),
            borderRadius: theme.shape.borderRadius,
            paddingTop: 0,
            paddingBottom: 0,
            borderColor: "transparent !important",
            lineHeight: 1.75,
            "&.Mui-selected": {
                background: theme.palette.background.paper,
                borderColor: "transparent",
                "&:hover": {
                    borderColor: theme.palette.action.active,
                },
            },
            "&:not(:first-of-type)": {
                borderRadius: theme.shape.borderRadius,
            },
            "&:first-of-type": {
                borderRadius: theme.shape.borderRadius,
            },
        },
    },
}));
function FieldInput({ actionHandler, field, path, }) {
    const { classes, cx } = useStyles();
    switch (field.input) {
        case "autocomplete":
            return (_jsx(Autocomplete, { className: classes.autocomplete, size: "small", freeSolo: true, value: field.value, disabled: field.disabled, readOnly: field.readonly, ListboxComponent: MenuList, ListboxProps: { dense: true }, renderOption: (props, option, { selected }) => (_jsx(MenuItem, { selected: selected, ...props, children: option })), componentsProps: {
                    clearIndicator: {
                        size: "small",
                        className: classes.clearIndicator,
                    },
                }, clearIcon: _jsx(CancelIcon, { fontSize: "small" }), renderInput: (params) => (_jsx(TextField, { ...params, variant: "filled", size: "small", placeholder: field.placeholder })), onInputChange: (_event, value, reason) => {
                    if (reason === "input") {
                        actionHandler({ action: "update", payload: { path, input: "autocomplete", value } });
                    }
                }, onChange: (_event, value) => {
                    actionHandler({
                        action: "update",
                        payload: { path, input: "autocomplete", value: value ?? undefined },
                    });
                }, options: field.items }));
        case "number":
            return (_jsx(NumberInput, { size: "small", variant: "filled", value: field.value, disabled: field.disabled, readOnly: field.readonly, placeholder: field.placeholder, fullWidth: true, max: field.max, min: field.min, precision: field.precision, step: field.step, onChange: (value) => {
                    actionHandler({ action: "update", payload: { path, input: "number", value } });
                } }));
        case "toggle":
            return (_jsx(ToggleButtonGroup, { className: classes.styledToggleButtonGroup, fullWidth: true, value: field.value ?? UNDEFINED_SENTINEL_VALUE, exclusive: true, disabled: field.disabled, size: "small", onChange: (_event, value) => {
                    if (value != undefined && field.readonly !== true) {
                        actionHandler({
                            action: "update",
                            payload: {
                                path,
                                input: "toggle",
                                value: value === UNDEFINED_SENTINEL_VALUE ? undefined : value,
                            },
                        });
                    }
                }, children: field.options.map((opt) => (_jsx(ToggleButton, { value: (typeof opt === "object" ? opt.value : opt) ?? UNDEFINED_SENTINEL_VALUE, children: typeof opt === "object" ? opt.label : opt }, (typeof opt === "object" ? opt.value : opt) ?? UNDEFINED_SENTINEL_VALUE))) }));
        case "string":
            return (_jsx(TextField, { variant: "filled", size: "small", fullWidth: true, disabled: field.disabled, value: field.value ?? "", placeholder: field.placeholder, InputProps: {
                    readOnly: field.readonly,
                }, onChange: (event) => {
                    actionHandler({
                        action: "update",
                        payload: { path, input: "string", value: event.target.value },
                    });
                } }));
        case "boolean":
            return (_jsxs(ToggleButtonGroup, { className: classes.styledToggleButtonGroup, fullWidth: true, value: field.value ?? false, exclusive: true, disabled: field.disabled, size: "small", onChange: (_event, value) => {
                    if (value != undefined && field.readonly !== true) {
                        actionHandler({
                            action: "update",
                            payload: { path, input: "boolean", value },
                        });
                    }
                }, children: [_jsx(ToggleButton, { value: false, children: "Off" }), _jsx(ToggleButton, { value: true, children: "On" })] }));
        case "rgb":
            return (_jsx(ColorPickerInput, { alphaType: "none", disabled: field.disabled, readOnly: field.readonly, placeholder: field.placeholder, value: field.value?.toString(), onChange: (value) => {
                    actionHandler({
                        action: "update",
                        payload: { path, input: "rgb", value },
                    });
                }, hideClearButton: field.hideClearButton }));
        case "rgba":
            return (_jsx(ColorPickerInput, { alphaType: "alpha", disabled: field.disabled, readOnly: field.readonly, placeholder: field.placeholder, value: field.value?.toString(), onChange: (value) => {
                    actionHandler({
                        action: "update",
                        payload: { path, input: "rgba", value },
                    });
                } }));
        case "messagepath":
            return (_jsx(MessagePathInput, { variant: "filled", path: field.value ?? "", disabled: field.disabled, readOnly: field.readonly, supportsMathModifiers: field.supportsMathModifiers, onChange: (value) => {
                    actionHandler({
                        action: "update",
                        payload: { path, input: "messagepath", value },
                    });
                }, validTypes: field.validTypes }));
        case "select": {
            const selectedOptionIndex = // use findIndex instead of find to avoid confusing TypeScript with union of arrays
             field.options.findIndex((option) => option.value === field.value);
            const selectedOption = field.options[selectedOptionIndex];
            const isEmpty = field.options.length === 0;
            let selectValue = field.value;
            if (!selectedOption) {
                selectValue = INVALID_SENTINEL_VALUE;
            }
            else if (selectValue == undefined) {
                // We can't pass value={undefined} or we get a React error "A component is changing an
                // uncontrolled input to be controlled" when changing the value to be non-undefined.
                selectValue = UNDEFINED_SENTINEL_VALUE;
            }
            const hasError = !selectedOption && (!isEmpty || field.value != undefined);
            return (_jsxs(Select, { className: cx({ [classes.error]: hasError }), size: "small", displayEmpty: true, fullWidth: true, disabled: field.disabled, readOnly: field.readonly, variant: "filled", value: selectValue, renderValue: (_value) => {
                    // Use field.value rather than the passed-in value so we can render the value even when
                    // it was not present in the list of options.
                    const value = field.value;
                    for (const option of field.options) {
                        if (option.value === value) {
                            return option.label.trim();
                        }
                    }
                    return value;
                }, onChange: (event) => {
                    actionHandler({
                        action: "update",
                        payload: {
                            path,
                            input: "select",
                            value: event.target.value === UNDEFINED_SENTINEL_VALUE
                                ? undefined
                                : event.target.value,
                        },
                    });
                }, MenuProps: { MenuListProps: { dense: true } }, children: [field.options.map(({ label, value = UNDEFINED_SENTINEL_VALUE, disabled }) => (_jsx(MenuItem, { value: value, disabled: disabled, children: label }, value))), isEmpty && _jsx(MenuItem, { disabled: true, children: "No options" }), !selectedOption && (_jsx(MenuItem, { style: { display: "none" }, value: INVALID_SENTINEL_VALUE }))] }));
        }
        case "gradient":
            return (_jsx(ColorGradientInput, { colors: field.value, disabled: field.disabled, readOnly: field.readonly, onChange: (value) => {
                    actionHandler({ action: "update", payload: { path, input: "gradient", value } });
                } }));
        case "vec3":
            return (_jsx(Vec3Input, { step: field.step, placeholder: field.placeholder, value: field.value, precision: field.precision, disabled: field.disabled, readOnly: field.readonly, min: field.min, max: field.max, onChange: (value) => {
                    actionHandler({ action: "update", payload: { path, input: "vec3", value } });
                } }));
        case "vec2":
            return (_jsx(Vec2Input, { step: field.step, value: field.value, placeholder: field.placeholder, precision: field.precision, disabled: field.disabled, readOnly: field.readonly, min: field.min, max: field.max, onChange: (value) => {
                    actionHandler({ action: "update", payload: { path, input: "vec2", value } });
                } }));
    }
}
function FieldLabel({ field }) {
    const { classes } = useStyles();
    if (field.input === "vec2") {
        const labels = field.labels ?? ["X", "Y"];
        return (_jsx(_Fragment, { children: _jsxs("div", { className: classes.multiLabelWrapper, children: [_jsx(Typography, { title: field.label, variant: "subtitle2", color: "text.secondary", noWrap: true, flex: "auto", children: field.label }), labels.map((label, index) => (_jsx(Typography, { title: field.label, variant: "subtitle2", color: "text.secondary", noWrap: true, style: { gridColumn: index === 0 ? "span 1" : "2 / span 1" }, flex: "auto", children: label }, label)))] }) }));
    }
    else if (field.input === "vec3") {
        const labels = field.labels ?? ["X", "Y", "Z"];
        return (_jsx(_Fragment, { children: _jsxs("div", { className: classes.multiLabelWrapper, children: [_jsx(Typography, { title: field.label, variant: "subtitle2", color: "text.secondary", noWrap: true, flex: "auto", children: field.label }), labels.map((label, index) => (_jsx(Typography, { title: field.label, variant: "subtitle2", color: "text.secondary", noWrap: true, style: { gridColumn: index === 0 ? "span 1" : "2 / span 1" }, flex: "auto", children: label }, label)))] }) }));
    }
    else {
        return (_jsx(_Fragment, { children: _jsx(Typography, { className: classes.fieldLabel, title: field.help ?? field.label, variant: "subtitle2", children: field.label }) }));
    }
}
function FieldEditorComponent({ actionHandler, field, path, }) {
    const indent = Math.min(path.length, 4);
    const paddingLeft = 0.75 + 2 * (indent - 1);
    const { classes, cx } = useStyles();
    const { renderSettingsStatusButton } = useAppContext();
    const statusButton = renderSettingsStatusButton ? renderSettingsStatusButton(field) : undefined;
    return (_jsxs(_Fragment, { children: [_jsxs(Stack, { direction: "row", alignItems: "center", justifyContent: "flex-end", gap: 0.5, paddingLeft: paddingLeft, fullHeight: true, children: [statusButton, field.error && (_jsx(Tooltip, { arrow: true, placement: "top", title: _jsx(Typography, { variant: "subtitle2", children: field.error }), children: _jsx(ErrorIcon, { color: "error", fontSize: "small" }) })), _jsx(FieldLabel, { field: field })] }), _jsx("div", { className: cx(classes.fieldWrapper, { [classes.error]: field.error != undefined }), children: _jsx(FieldInput, { actionHandler: actionHandler, field: field, path: path }) }), _jsx(Stack, { paddingBottom: 0.25, style: { gridColumn: "span 2" } })] }));
}
export const FieldEditor = React.memo(FieldEditorComponent);
