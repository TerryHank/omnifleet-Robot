import { jsxs as _jsxs, jsx as _jsx, Fragment as _Fragment } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { Typography, Link, Divider } from "@mui/material";
import { useMemo, useState } from "react";
import { makeStyles } from "tss-react/mui";
import Stack from "@foxglove/studio-base/components/Stack";
const useStyles = makeStyles()((theme) => ({
    grid: {
        display: "grid",
        gridTemplateRows: "auto 1fr auto",
        height: "100%",
        padding: theme.spacing(2),
        overflowY: "auto",
    },
    errorDetailStack: {
        fontSize: theme.typography.body2.fontSize,
        lineHeight: "1.3em",
        paddingLeft: theme.spacing(2),
    },
    errorDetailContainer: {
        overflowY: "auto",
        background: theme.palette.background.paper,
        padding: theme.spacing(1),
        minHeight: theme.spacing(10),
    },
    actions: {
        flex: "auto",
        paddingTop: theme.spacing(2),
        textAlign: "right",
    },
}));
/**
 * Remove source locations (which often include file hashes) so storybook screenshots can be
 * deterministic.
 */
function sanitizeStack(stack) {
    return stack.replace(/\s+\(.+\)$/gm, "").replace(/\s+https?:\/\/.+$/gm, "");
}
function ErrorStacktrace({ stack, hideSourceLocations, }) {
    const { classes } = useStyles();
    const lines = (hideSourceLocations ? sanitizeStack(stack) : stack)
        .trim()
        .replace(/^\s*at /gm, "")
        .split("\n")
        .map((line) => line.trim());
    return (_jsx("pre", { className: classes.errorDetailStack, children: lines.map((line, i) => {
            const match = /^(.+)\s(\(.+$)/.exec(line);
            if (!match) {
                return line + "\n";
            }
            return (_jsxs("span", { children: [_jsxs("span", { children: [match[1], " "] }), _jsx("span", { children: match[2] }), "\n"] }, i));
        }) }));
}
function ErrorDisplay(props) {
    const { classes } = useStyles();
    const { error, errorInfo, hideErrorSourceLocations = false } = props;
    const [showErrorDetails, setShowErrorDetails] = useState(props.showErrorDetails ?? false);
    const errorDetails = useMemo(() => {
        if (!showErrorDetails) {
            return ReactNull;
        }
        let stackWithoutMessage = error?.stack ?? "";
        const errorString = error?.toString() ?? "";
        if (stackWithoutMessage.startsWith(errorString)) {
            stackWithoutMessage = stackWithoutMessage.substring(errorString.length);
        }
        return (_jsxs("div", { children: [_jsx(Typography, { fontWeight: "bold", children: "Error stack:" }), _jsx(ErrorStacktrace, { stack: stackWithoutMessage, hideSourceLocations: hideErrorSourceLocations }), errorInfo && (_jsxs(_Fragment, { children: [_jsx(Typography, { fontWeight: "bold", children: "Component stack:" }), _jsx(ErrorStacktrace, { stack: errorInfo.componentStack, hideSourceLocations: hideErrorSourceLocations })] }))] }));
    }, [error, errorInfo, hideErrorSourceLocations, showErrorDetails]);
    return (_jsxs("div", { className: classes.grid, children: [_jsxs(Stack, { gap: 2, paddingBottom: 2, children: [_jsxs(Stack, { children: [_jsx(Typography, { variant: "h4", gutterBottom: true, children: props.title ?? "The app encountered an unexpected error" }), _jsx(Typography, { variant: "body1", children: props.content })] }), _jsx(Divider, {}), _jsx(Typography, { variant: "subtitle2", component: "code", fontWeight: "bold", children: error?.message }), _jsxs(Link, { color: "secondary", onClick: () => {
                            setShowErrorDetails(!showErrorDetails);
                        }, children: [showErrorDetails ? "Hide" : "Show", " details"] })] }), errorDetails && _jsx("div", { className: classes.errorDetailContainer, children: errorDetails }), !errorDetails && _jsx("div", {}), _jsx("div", { className: classes.actions, children: props.actions })] }));
}
export default ErrorDisplay;
