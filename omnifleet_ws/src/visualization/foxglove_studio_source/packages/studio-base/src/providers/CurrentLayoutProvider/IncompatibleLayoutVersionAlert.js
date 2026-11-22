import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, Link, } from "@mui/material";
import { useTranslation } from "react-i18next";
import isDesktopApp from "@foxglove/studio-base/util/isDesktopApp";
export function IncompatibleLayoutVersionAlert(props) {
    const { isDesktop, onClose } = props;
    const { t } = useTranslation("incompatibleLayoutVersion");
    const showDesktopText = isDesktop ?? isDesktopApp();
    return (_jsxs(Dialog, { open: true, onClose: onClose, children: [_jsx(DialogTitle, { children: t("title") }), _jsxs(DialogContent, { children: [showDesktopText && (_jsxs(DialogContentText, { children: [t("desktopText"), _jsx(Link, { target: "_blank", href: "https://foxglove.dev/download", children: "https://foxglove.dev/download" }), "."] })), !showDesktopText && _jsx(DialogContentText, { children: t("webText") })] }), _jsx(DialogActions, { children: _jsx(Button, { onClick: onClose, variant: "contained", children: "OK" }) })] }));
}
