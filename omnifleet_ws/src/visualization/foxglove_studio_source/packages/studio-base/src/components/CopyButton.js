import { jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { Copy16Regular, Copy20Regular, Copy24Regular, Checkmark16Filled, Checkmark20Filled, Checkmark24Filled, } from "@fluentui/react-icons";
import { Button, IconButton, Tooltip, Typography, useTheme, } from "@mui/material";
import { useCallback, useState, useMemo } from "react";
import clipboard from "@foxglove/studio-base/util/clipboard";
function CopyButtonComponent(props) {
    const { children, className, color = "primary", edge, size = "medium", iconSize = "medium", getText, } = props;
    const theme = useTheme();
    const [copied, setCopied] = useState(false);
    const checkIcon = useMemo(() => {
        switch (iconSize) {
            case "small":
                return _jsx(Checkmark16Filled, { primaryFill: theme.palette.success.main });
            case "medium":
                return _jsx(Checkmark20Filled, { primaryFill: theme.palette.success.main });
            case "large":
                return _jsx(Checkmark24Filled, { primaryFill: theme.palette.success.main });
        }
    }, [iconSize, theme.palette.success.main]);
    const copyIcon = useMemo(() => {
        switch (iconSize) {
            case "small":
                return _jsx(Copy16Regular, {});
            case "medium":
                return _jsx(Copy20Regular, {});
            case "large":
                return _jsx(Copy24Regular, {});
        }
    }, [iconSize]);
    const handleCopy = useCallback(() => {
        clipboard
            .copy(getText())
            .then(() => {
            setCopied(true);
            setTimeout(() => {
                setCopied(false);
            }, 1500);
        })
            .catch((err) => {
            console.warn(err);
        });
    }, [getText]);
    if (children == undefined) {
        return (_jsx(Tooltip, { arrow: true, title: copied ? "Copied" : "Copy to clipboard", children: _jsx(IconButton, { edge: edge, className: className, size: size, onClick: handleCopy, color: copied ? "success" : color, children: copied ? checkIcon : copyIcon }) }));
    }
    return (_jsx(Button, { size: size, className: className, onClick: handleCopy, color: "inherit", startIcon: copied ? checkIcon : copyIcon, children: _jsx(Typography, { color: copied ? "text.primary" : color, variant: "body2", children: children }) }));
}
export default React.memo(CopyButtonComponent);
