import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import CancelIcon from "@mui/icons-material/Cancel";
import { TextField, Popover, IconButton, inputBaseClasses, Tooltip } from "@mui/material";
import { useCallback, useState } from "react";
import { makeStyles } from "tss-react/mui";
import Stack from "@foxglove/studio-base/components/Stack";
import { ColorPickerControl, useColorPickerControl } from "./ColorPickerControl";
import { ColorSwatch } from "./ColorSwatch";
const useStyles = makeStyles()((theme, _params, classes) => ({
    root: {
        position: "relative",
    },
    rootDisabled: {
        pointerEvents: "none",
    },
    textField: {
        [`.${inputBaseClasses.formControl}.${inputBaseClasses.root}`]: {
            padding: 0,
        },
        [`.${inputBaseClasses.root}`]: {
            fontFamily: theme.typography.fontMonospace,
            cursor: "pointer",
            [`:not(:hover) .${classes.iconButton}`]: {
                visibility: "hidden",
            },
        },
        [`.${inputBaseClasses.input}`]: {
            alignItems: "center",
            fontFeatureSettings: `${theme.typography.fontFeatureSettings}, "zero"`,
        },
    },
    iconButton: {
        marginRight: theme.spacing(0.25),
        opacity: theme.palette.action.disabledOpacity,
        ":hover": {
            background: "transparent",
            opacity: 1,
        },
    },
    colorSwatch: {
        marginLeft: theme.spacing(0.75),
    },
}));
export function ColorPickerInput(props) {
    const { alphaType, disabled, onChange, readOnly, hideClearButton, value } = props;
    const { classes, cx } = useStyles();
    const { swatchColor, displayValue, updatePrefixedColor, editedValueIsInvalid, editedValue, updateEditedValue, onInputBlur, } = useColorPickerControl({
        alphaType,
        onChange,
        value,
    });
    const [anchorElement, setAnchorElement] = useState(undefined);
    const handleClick = useCallback((event) => {
        setAnchorElement(event.currentTarget);
    }, []);
    const handleClose = useCallback(() => {
        setAnchorElement(undefined);
    }, []);
    const clearValue = useCallback(() => {
        onChange(undefined);
    }, [onChange]);
    const open = Boolean(anchorElement);
    const shouldHideClearButton = (displayValue ?? "") === "" || (hideClearButton ?? false);
    return (_jsxs(Stack, { className: cx(classes.root, {
            [classes.rootDisabled]: disabled === true || readOnly === true,
        }), children: [_jsx(TextField, { className: classes.textField, fullWidth: true, disabled: disabled, placeholder: props.placeholder, size: "small", variant: "filled", value: editedValue ? `#${editedValue.replace("#", "")}` : editedValue, onKeyDown: (event) => event.key === "Enter" && handleClose, onChange: (event) => {
                    updateEditedValue(event.target.value);
                }, onBlur: onInputBlur, InputProps: {
                    onFocus: (event) => {
                        event.target.select();
                    },
                    // readOnly: true,
                    startAdornment: (_jsx(ColorSwatch, { className: classes.colorSwatch, color: swatchColor, onClick: handleClick, size: "small" })),
                    endAdornment: !shouldHideClearButton && (_jsx(Tooltip, { title: "\u6062\u590D\u9ED8\u8BA4\u503C", children: _jsx(IconButton, { size: "small", className: classes.iconButton, onClick: clearValue, disabled: disabled, children: _jsx(CancelIcon, { fontSize: "inherit" }) }) })),
                } }), _jsx(Popover, { open: open, anchorEl: anchorElement, onClose: handleClose, anchorOrigin: {
                    vertical: "bottom",
                    horizontal: "left",
                }, transformOrigin: {
                    vertical: "top",
                    horizontal: "center",
                }, children: _jsx(ColorPickerControl, { alphaType: alphaType, onChange: onChange, onEnterKey: handleClose, swatchColor: swatchColor, updatePrefixedColor: updatePrefixedColor, editedValueIsInvalid: editedValueIsInvalid, editedValue: editedValue, updateEditedValue: updateEditedValue, onInputBlur: onInputBlur }) })] }));
}
