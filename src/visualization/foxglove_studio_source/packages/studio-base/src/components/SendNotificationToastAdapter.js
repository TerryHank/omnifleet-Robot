import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { Link } from "@mui/material";
import { useSnackbar } from "notistack";
import { useLayoutEffect, useState } from "react";
import NotificationModal from "@foxglove/studio-base/components/NotificationModal";
import { setNotificationHandler, unsetNotificationHandler, } from "@foxglove/studio-base/util/sendNotification";
const severityToToastAppearance = (severity) => {
    switch (severity) {
        case "error":
            return "error";
        case "warn":
            return "warning";
        case "info":
            return "default";
        default:
            return "default";
    }
};
export default function SendNotificationToastAdapter() {
    const { enqueueSnackbar } = useSnackbar();
    const [notificationDetails, setNotificationDetails] = useState(undefined);
    useLayoutEffect(() => {
        setNotificationHandler((message, details, _type, severity) => {
            enqueueSnackbar(_jsxs("div", { children: [message, " ", _jsx(Link, { onClick: () => {
                            setNotificationDetails({ message, details, severity });
                        }, variant: "inherit", fontStyle: "italic", color: "inherit", underline: "hover", children: "(see details)" })] }), {
                variant: severityToToastAppearance(severity),
                persist: severity === "error",
            });
        });
        return () => {
            unsetNotificationHandler();
        };
    }, [enqueueSnackbar]);
    if (notificationDetails == undefined) {
        return _jsx(_Fragment, {});
    }
    return (_jsx(NotificationModal, { notification: notificationDetails, onRequestClose: () => {
            setNotificationDetails(undefined);
        } }));
}
