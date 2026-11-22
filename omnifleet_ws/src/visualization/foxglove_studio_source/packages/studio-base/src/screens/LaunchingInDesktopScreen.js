import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { Link, Typography } from "@mui/material";
import { useEffect } from "react";
import { useSessionStorageValue } from "@foxglove/hooks";
import { AppSetting } from "@foxglove/studio-base/AppSetting";
import Stack from "@foxglove/studio-base/components/Stack";
import { LaunchPreferenceValue } from "@foxglove/studio-base/types/LaunchPreferenceValue";
export function LaunchingInDesktopScreen() {
    const [, setLaunchPreference] = useSessionStorageValue(AppSetting.LAUNCH_PREFERENCE);
    const cleanWebURL = new URL(window.location.href);
    cleanWebURL.searchParams.delete("openIn");
    function openWeb() {
        setLaunchPreference(LaunchPreferenceValue.WEB);
        window.location.href = cleanWebURL.href;
    }
    useEffect(() => {
        const desktopURL = new URL("foxglove://open");
        cleanWebURL.searchParams.forEach((v, k) => {
            if (k && v) {
                desktopURL.searchParams.set(k, v);
                // Temporarily send both sets of params until desktop app is updated to
                // use new ds.* parameters.
                switch (k) {
                    case "ds":
                        desktopURL.searchParams.set("type", v);
                        break;
                    case "ds.deviceId":
                        desktopURL.searchParams.set("deviceId", v);
                        break;
                    case "ds.importId":
                        desktopURL.searchParams.set("importId", v);
                        break;
                    case "ds.end":
                        desktopURL.searchParams.set("end", v);
                        break;
                    case "ds.start":
                        desktopURL.searchParams.set("start", v);
                        break;
                    case "ds.url":
                        desktopURL.searchParams.set("url", v);
                        break;
                    case "time":
                        desktopURL.searchParams.set("seekTo", v);
                        break;
                }
            }
        });
        window.location.href = desktopURL.href;
    });
    return (_jsx(Stack, { alignItems: "center", justifyContent: "center", fullHeight: true, children: _jsxs(Stack, { alignItems: "center", justifyContent: "center", fullHeight: true, gap: 2.5, style: { maxWidth: 480 }, children: [_jsx(Typography, { align: "center", variant: "h2", fontWeight: 600, children: "Launching Foxglove Studio\u2026" }), _jsx(Typography, { align: "center", fontWeight: 600, children: "We\u2019ve directed you to the desktop app." }), _jsxs(Stack, { gap: 0.5, children: [_jsxs(Typography, { align: "center", children: ["You can also", " ", _jsx(Link, { color: "primary", underline: "hover", onClick: openWeb, children: "open this link in your browser" }), "."] }), _jsxs(Typography, { align: "center", children: ["Don\u2019t have the app installed?\u00A0", _jsx(Link, { color: "primary", underline: "hover", href: "https://foxglove.dev/download", target: "_blank", children: "Download Foxglove Studio" })] })] })] }) }));
}
