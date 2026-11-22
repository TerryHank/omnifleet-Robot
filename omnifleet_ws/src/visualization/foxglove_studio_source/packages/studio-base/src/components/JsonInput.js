import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
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
import ErrorIcon from "@mui/icons-material/Error";
import { Typography } from "@mui/material";
import CodeEditor from "@uiw/react-textarea-code-editor";
import * as _ from "lodash-es";
import { makeStyles } from "tss-react/mui";
import Stack from "@foxglove/studio-base/components/Stack";
import { validationErrorToString } from "@foxglove/studio-base/util/validators";
const { useState, useCallback, useRef, useLayoutEffect, useEffect } = React;
const useStyles = makeStyles()((theme) => ({
    editor: {
        backgroundColor: "transparent !important",
        font: "inherit !important",
        fontFamily: `${theme.typography.fontMonospace} !important`,
        overflow: "auto",
    },
    error: {
        "*": {
            color: `${theme.palette.error.main} !important`,
        },
    },
}));
/**
 * Handles value change, data validation, and data stringifying/parsing.
 * Any external value change will cause the input string to change and trigger new validations.
 * Only valid internal value change will call onChange. Any data processing and validation error will trigger onError.
 */
function ValidatedInputBase({ dataTestId, dataValidator = () => undefined, onChange, onError, parse, readOnly = false, maxHeight, stringify, value, }) {
    const { classes, cx } = useStyles();
    const [error, setError] = useState("");
    const [inputStr, setInputStr] = useState("");
    const prevIncomingVal = useRef("");
    const inputRef = useRef(ReactNull);
    const [isEditing, setIsEditing] = useState(false);
    // validate the input string, and setError or call onChange if needed
    const memorizedInputValidation = useCallback((newInputVal, onChangeFcn) => {
        let newVal;
        let newError;
        // parse the empty string directly as empty array or object for validation and onChange callback
        if (newInputVal.trim() === "") {
            newVal = Array.isArray(value) ? [] : {};
        }
        else {
            try {
                newVal = parse(newInputVal);
            }
            catch (e) {
                newError = e.message;
            }
        }
        if (newError != undefined) {
            setError(newError);
            return;
        }
        setError(""); // clear the previous error
        const validationResult = dataValidator(newVal);
        if (validationResult != undefined) {
            setError(validationErrorToString(validationResult));
            return;
        }
        if (onChangeFcn) {
            onChangeFcn(newVal);
        }
    }, [dataValidator, parse, value]);
    /**
     * when not in editing mode whenever the incoming value changes
     * we'll compare the new value with prevIncomingVal and reset local state values if they are different
     */
    useLayoutEffect(() => {
        if (!isEditing && value !== prevIncomingVal.current) {
            if (_.isEqual(value, prevIncomingVal.current)) {
                return;
            }
            let newVal = "";
            let newError;
            try {
                newVal = stringify(value);
            }
            catch (e) {
                newError = `Error stringifying the new value, using "" as default. ${e.message}`;
            }
            setInputStr(newVal);
            prevIncomingVal.current = value;
            if (newError != undefined) {
                setError(newError);
                return;
            }
            // try to validate if successfully stringified the new value
            memorizedInputValidation(newVal);
        }
    }, [value, stringify, memorizedInputValidation, isEditing]);
    const handleChange = useCallback((e) => {
        const val = e.currentTarget.value;
        if (!isEditing) {
            setIsEditing(true);
        }
        setInputStr(val);
        memorizedInputValidation(val, onChange);
    }, [isEditing, memorizedInputValidation, onChange]);
    useEffect(() => {
        if (onError && error.length > 0) {
            onError(error);
        }
    }, [error, onError]);
    // scroll to the bottom when the text gets too long
    useLayoutEffect(() => {
        if (!isEditing) {
            const inputElem = inputRef.current;
            if (inputElem) {
                inputElem.scrollTop = inputElem.scrollHeight;
            }
        }
    }, [isEditing, inputStr]);
    return (_jsxs(_Fragment, { children: [_jsx(CodeEditor, { className: cx(classes.editor, { [classes.error]: error.length > 0 }), readOnly: readOnly, "data-testid": dataTestId ?? `validated-input-${JSON.stringify(inputStr)}`, ref: inputRef, value: inputStr, onChange: handleChange, language: "json", onBlur: () => {
                    setIsEditing(false);
                }, padding: 12, style: { maxHeight: maxHeight ?? 300 } }), error.length > 0 && (_jsxs(Stack, { direction: "row", alignItems: "center", gap: 0.25, padding: 0.5, children: [_jsx(ErrorIcon, { fontSize: "inherit", color: "error" }), _jsx(Typography, { variant: "caption", color: "error.main", children: error })] }))] }));
}
export default function JsonInput(props) {
    function stringify(val) {
        if (val === '""') {
            return val;
        }
        return JSON.stringify(val, undefined, 2) ?? "";
    }
    return (_jsx(Stack, { children: _jsx(ValidatedInputBase, { parse: JSON.parse, stringify: stringify, ...props, maxHeight: "none" }) }));
}
