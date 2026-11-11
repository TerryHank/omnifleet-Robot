import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { ArrowDownload20Filled, Delete20Regular } from "@fluentui/react-icons";
import CloseIcon from "@mui/icons-material/Close";
import { Button, IconButton, Dialog, DialogContent, DialogActions, DialogTitle, TextField, outlinedInputClasses, } from "@mui/material";
import { useCallback, useMemo, useState } from "react";
import { makeStyles } from "tss-react/mui";
import CopyButton from "@foxglove/studio-base/components/CopyButton";
import HoverableIconButton from "@foxglove/studio-base/components/HoverableIconButton";
import Stack from "@foxglove/studio-base/components/Stack";
import { downloadTextFile } from "@foxglove/studio-base/util/download";
const useStyles = makeStyles()((theme) => ({
    textarea: {
        [`.${outlinedInputClasses.root}`]: {
            backgroundColor: theme.palette.action.hover,
            fontFamily: theme.typography.fontMonospace,
            maxHeight: "60vh",
            overflowY: "auto",
            padding: theme.spacing(0.25),
        },
    },
    dialogTitle: {
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
    },
}));
export function ShareJsonModal({ initialValue = {}, onChange, onRequestClose, title, }) {
    const { classes } = useStyles();
    const [value, setValue] = useState(JSON.stringify(initialValue, undefined, 2) ?? "");
    const { decodedValue, error } = useMemo(() => {
        try {
            return { decodedValue: JSON.parse(value === "" ? "{}" : value), error: undefined };
        }
        catch (err) {
            return { decodedValue: undefined, error: err };
        }
    }, [value]);
    const handleSubmit = useCallback(() => {
        onChange(decodedValue);
        onRequestClose();
    }, [decodedValue, onChange, onRequestClose]);
    const handleDownload = useCallback(() => {
        downloadTextFile(value, "layout.json");
    }, [value]);
    const getText = useCallback(() => value, [value]);
    return (_jsxs(Dialog, { open: true, onClose: onRequestClose, maxWidth: "sm", fullWidth: true, children: [_jsxs(DialogTitle, { className: classes.dialogTitle, children: [title, _jsx(IconButton, { onClick: onRequestClose, edge: "end", children: _jsx(CloseIcon, {}) })] }), _jsx(DialogContent, { children: _jsx(TextField, { className: classes.textarea, fullWidth: true, multiline: true, rows: 10, value: value, onChange: (event) => {
                        setValue(event.target.value);
                    }, autoFocus: true, error: error != undefined, helperText: error ? "The JSON provided is invalid." : " " // pass whitespace to prevent height from jumping
                    , inputProps: { "data-testid": "share-json-input" }, FormHelperTextProps: { variant: "standard" }, spellCheck: false }) }), _jsxs(DialogActions, { children: [_jsxs(Stack, { direction: "row", gap: 1, children: [_jsx(IconButton, { onClick: handleDownload, title: "\u4E0B\u8F7D", "aria-label": "\u4E0B\u8F7D", children: _jsx(ArrowDownload20Filled, {}) }), _jsx(CopyButton, { color: "inherit", getText: getText }), _jsx(HoverableIconButton, { activeColor: "error", onClick: () => {
                                    setValue("{}");
                                }, title: "\u6E05\u9664", "aria-label": "\u6E05\u9664", icon: _jsx(Delete20Regular, {}) })] }), _jsx(Stack, { flex: "auto" }), _jsx(Button, { disabled: error != undefined, variant: "contained", onClick: handleSubmit, children: "Apply" })] })] }));
}
