import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
//
// This file incorporates work covered by the following copyright and
// permission notice:
//
//   Copyright 2018-2021 Cruise LLC
//
//   This source code is licensed under the Apache License, Version 2.0,
//   found at http://www.apache.org/licenses/LICENSE-2.0
//   You may not use this file except in compliance with the License.
import { Dialog, DialogContent, DialogTitle, DialogActions, Button } from "@mui/material";
import { useCallback, useEffect, useRef, useState } from "react";
import { useKeyPressEvent } from "react-use";
function ConfirmModal(props) {
    const originalOnComplete = props.onComplete;
    const completed = useRef(false);
    const onComplete = useCallback((result) => {
        if (!completed.current) {
            completed.current = true;
            originalOnComplete(result);
        }
    }, [originalOnComplete]);
    useKeyPressEvent("Enter", () => {
        onComplete("ok");
    });
    // Ensure we still call onComplete(undefined) when the component unmounts, if it hasn't been
    // called already
    useEffect(() => {
        return () => {
            onComplete("cancel");
        };
    }, [onComplete]);
    const buttons = [
        props.cancel !== false && (_jsx(Button, { variant: "outlined", color: "inherit", onClick: () => {
                onComplete("cancel");
            }, children: props.cancel ?? "Cancel" }, "cancel")),
        _jsx(Button, { variant: "contained", color: props.variant === "danger" ? "error" : "primary", type: "submit", children: props.ok ?? "OK" }, "confirm"),
    ];
    if (props.variant === "danger") {
        buttons.reverse();
    }
    return (_jsx(Dialog, { open: true, onClose: () => {
            onComplete("cancel");
        }, maxWidth: "xs", fullWidth: true, children: _jsxs("form", { onSubmit: (event) => {
                event.preventDefault();
                onComplete("ok");
            }, children: [_jsx(DialogTitle, { children: props.title }), _jsx(DialogContent, { children: props.prompt }), _jsx(DialogActions, { children: buttons })] }) }));
}
// Returns a function that can be used similarly to the DOM confirm(), but
// backed by a React element rather than a native modal, and asynchronous.
export function useConfirm() {
    const [modal, setModal] = useState();
    const openConfirm = useCallback(async (options) => {
        return await new Promise((resolve) => {
            setModal(_jsx(ConfirmModal, { ...options, onComplete: (value) => {
                    resolve(value);
                    setModal(undefined);
                } }));
        });
    }, []);
    return [openConfirm, modal];
}
