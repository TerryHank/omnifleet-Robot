import { jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import { IconButton, TextField } from "@mui/material";
import * as _ from "lodash-es";
import { useCallback, useRef } from "react";
import { useLatest } from "react-use";
import { makeStyles } from "tss-react/mui";
const Constants = {
    ScrubPrecision: 4,
};
const useStyles = makeStyles()((theme) => ({
    iconButton: {
        "&.MuiIconButton-edgeStart": {
            marginLeft: theme.spacing(-0.75),
            borderTopRightRadius: 0,
            borderBottomRightRadius: 0,
        },
        "&.MuiIconButton-edgeEnd": {
            marginRight: theme.spacing(-0.75),
            borderTopLeftRadius: 0,
            borderBottomLeftRadius: 0,
        },
    },
    textField: {
        ".MuiInputBase-formControl.MuiInputBase-root": {
            paddingTop: 0,
            paddingBottom: 0,
        },
        ".MuiInputBase-input": {
            textAlign: "center",
            fontFamily: theme.typography.fontMonospace,
            cursor: "ew-resize",
            "&::-webkit-outer-spin-button, &::-webkit-inner-spin-button": {
                appearance: "none",
                margin: 0,
            },
        },
        "@media (pointer: fine)": {
            ".MuiIconButton-root": {
                visibility: "hidden",
            },
            "&:hover .MuiIconButton-root": {
                visibility: "visible",
            },
        },
    },
    textFieldReadonly: {
        ".MuiInputBase-input": {
            cursor: "auto",
        },
    },
}));
export function NumberInput(props) {
    const { classes, cx } = useStyles();
    const { value, iconDown, iconUp, step = 1, min, max, onChange, disabled, readOnly, precision = 100, } = props;
    const inputRef = useRef(ReactNull);
    // Maintain our own internal scrub value during the scrub to prevent jitter.
    const scrubValue = useRef(0);
    const latestValue = useLatest(value);
    const placeHolderValue = _.isFinite(Number(props.placeholder))
        ? Number(props.placeholder)
        : undefined;
    const updateValue = useCallback((newValue) => {
        if (disabled === true || readOnly === true) {
            return;
        }
        const clampedValue = newValue == undefined
            ? undefined
            : _.clamp(newValue, min ?? Number.NEGATIVE_INFINITY, max ?? Number.POSITIVE_INFINITY);
        onChange(clampedValue != undefined ? _.round(clampedValue, precision) : clampedValue);
    }, [disabled, readOnly, min, max, onChange, precision]);
    const isDragging = useRef(false);
    const onPointerDown = useCallback((event) => {
        isDragging.current = true;
        event.currentTarget.setPointerCapture(event.pointerId);
        const scrubStart = latestValue.current ?? placeHolderValue ?? 0;
        scrubValue.current = _.isFinite(scrubStart) ? scrubStart : 0;
    }, [latestValue, placeHolderValue]);
    const onPointerUp = useCallback((event) => {
        isDragging.current = false;
        event.currentTarget.releasePointerCapture(event.pointerId);
    }, []);
    const onPointerMove = useCallback((event) => {
        if (event.buttons !== 1 || !isDragging.current) {
            return;
        }
        event.preventDefault();
        event.currentTarget.blur();
        const scale = event.shiftKey ? 10 : 1;
        const delta = Math.sign(event.movementX) * Math.pow(Math.abs(event.movementX), 1.5) * 0.1 * step * scale;
        scrubValue.current = _.round(scrubValue.current + delta, Constants.ScrubPrecision);
        updateValue(scrubValue.current);
    }, [step, updateValue]);
    const displayValue = inputRef.current === document.activeElement
        ? value
        : value != undefined
            ? _.round(value, precision)
            : undefined;
    return (_jsx(TextField, { ...props, value: displayValue ?? "", onChange: (event) => {
            updateValue(event.target.value.length > 0 ? Number(event.target.value) : undefined);
        }, type: "number", className: cx(classes.textField, { [classes.textFieldReadonly]: readOnly }), inputProps: {
            ref: inputRef,
            step,
            onPointerDown,
            onPointerUp,
            onPointerMove,
        }, InputProps: {
            readOnly,
            startAdornment: (_jsx(IconButton, { className: classes.iconButton, size: "small", edge: "start", tabIndex: -1, onClick: (event) => {
                    updateValue((value ?? placeHolderValue ?? 0) - (event.shiftKey ? step * 10 : step));
                }, children: iconDown ?? _jsx(ChevronLeftIcon, { fontSize: "small" }) })),
            endAdornment: (_jsx(IconButton, { className: classes.iconButton, size: "small", edge: "end", tabIndex: -1, onClick: (event) => {
                    updateValue((value ?? placeHolderValue ?? 0) + (event.shiftKey ? step * 10 : step));
                }, children: iconUp ?? _jsx(ChevronRightIcon, { fontSize: "small" }) })),
        } }));
}
