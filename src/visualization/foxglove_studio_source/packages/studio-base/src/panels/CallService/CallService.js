import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { Button, TextField, Tooltip, Typography, inputBaseClasses } from "@mui/material";
import { useCallback, useEffect, useMemo, useState } from "react";
import { makeStyles } from "tss-react/mui";
import Log from "@foxglove/log";
import Stack from "@foxglove/studio-base/components/Stack";
import ThemeProvider from "@foxglove/studio-base/theme/ThemeProvider";
import { defaultConfig, settingsActionReducer, useSettingsTree } from "./settings";
const log = Log.getLogger(__dirname);
const useStyles = makeStyles()((theme, { buttonColor }) => {
    const augmentedButtonColor = buttonColor
        ? theme.palette.augmentColor({
            color: { main: buttonColor },
        })
        : undefined;
    return {
        button: {
            backgroundColor: augmentedButtonColor?.main,
            color: augmentedButtonColor?.contrastText,
            "&:hover": {
                backgroundColor: augmentedButtonColor?.dark,
            },
        },
        textarea: {
            height: "100%",
            [`.${inputBaseClasses.root}`]: {
                backgroundColor: theme.palette.background.paper,
                height: "100%",
                overflow: "hidden",
                padding: theme.spacing(1, 0.5),
                textAlign: "left",
                width: "100%",
                [`.${inputBaseClasses.input}`]: {
                    height: "100% !important",
                    lineHeight: 1.4,
                    fontFamily: theme.typography.fontMonospace,
                    overflow: "auto !important",
                    resize: "none",
                },
            },
        },
    };
});
function parseInput(value) {
    let parsedObject;
    let error = undefined;
    try {
        const parsedAny = JSON.parse(value);
        if (Array.isArray(parsedAny)) {
            error = "Request content must be an object, not an array";
        }
        else if (parsedAny == undefined) {
            error = "Request content must be an object, not null";
        }
        else if (typeof parsedAny !== "object") {
            error = `Request content must be an object, not ‘${typeof parsedAny}’`;
        }
        else {
            parsedObject = parsedAny;
        }
    }
    catch (e) {
        error = value.length !== 0 ? e.message : "Enter valid request content as JSON";
    }
    return { error, parsedObject };
}
// Wrapper component with ThemeProvider so useStyles in the panel receives the right theme.
export function CallService({ context }) {
    const [colorScheme, setColorScheme] = useState("light");
    return (_jsx(ThemeProvider, { isDark: colorScheme === "dark", children: _jsx(CallServiceContent, { context: context, setColorScheme: setColorScheme }) }));
}
function CallServiceContent(props) {
    const { context, setColorScheme } = props;
    // panel extensions must notify when they've completed rendering
    // onRender will setRenderDone to a done callback which we can invoke after we've rendered
    const [renderDone, setRenderDone] = useState(() => () => { });
    const [state, setState] = useState();
    const [config, setConfig] = useState(() => ({
        ...defaultConfig,
        ...context.initialState,
    }));
    const { classes } = useStyles({ buttonColor: config.buttonColor });
    useEffect(() => {
        context.saveState(config);
        context.setDefaultPanelTitle(config.serviceName ? `Call service ${config.serviceName}` : undefined);
    }, [config, context]);
    useEffect(() => {
        context.watch("colorScheme");
        context.onRender = (renderState, done) => {
            setRenderDone(() => done);
            setColorScheme(renderState.colorScheme ?? "light");
        };
        return () => {
            context.onRender = undefined;
        };
    }, [context, setColorScheme]);
    const { error: requestParseError, parsedObject } = useMemo(() => parseInput(config.requestPayload ?? ""), [config.requestPayload]);
    const settingsActionHandler = useCallback((action) => {
        setConfig((prevConfig) => settingsActionReducer(prevConfig, action));
    }, [setConfig]);
    const settingsTree = useSettingsTree(config);
    useEffect(() => {
        context.updatePanelSettingsEditor({
            actionHandler: settingsActionHandler,
            nodes: settingsTree,
        });
    }, [context, settingsActionHandler, settingsTree]);
    const statusMessage = useMemo(() => {
        if (context.callService == undefined) {
            return "Connect to a data source that supports calling services";
        }
        if (!config.serviceName) {
            return "Configure a service in the panel settings";
        }
        return undefined;
    }, [context, config.serviceName]);
    const canCallService = Boolean(context.callService != undefined &&
        config.requestPayload &&
        config.serviceName &&
        parsedObject != undefined &&
        state?.status !== "requesting");
    const callServiceClicked = useCallback(async () => {
        if (!context.callService) {
            setState({ status: "error", value: "The data source does not allow calling services" });
            return;
        }
        try {
            setState({ status: "requesting", value: `Calling ${config.serviceName}...` });
            const response = await context.callService(config.serviceName, JSON.parse(config.requestPayload));
            setState({
                status: "success",
                value: JSON.stringify(response, 
                // handle stringify BigInt correctly
                (_key, value) => (typeof value === "bigint" ? value.toString() : value), 2) ?? "",
            });
        }
        catch (err) {
            setState({ status: "error", value: err.message });
            log.error(err);
        }
    }, [context, config.serviceName, config.requestPayload]);
    // Indicate render is complete - the effect runs after the dom is updated
    useEffect(() => {
        renderDone();
    }, [renderDone]);
    return (_jsxs(Stack, { flex: "auto", gap: 1, padding: 1.5, position: "relative", fullHeight: true, children: [_jsxs(Stack, { gap: 1, flexGrow: "1", direction: config.layout === "horizontal" ? "row" : "column", children: [_jsxs(Stack, { flexGrow: "1", children: [_jsx(Typography, { variant: "caption", noWrap: true, children: "Request" }), _jsx(TextField, { variant: "outlined", className: classes.textarea, multiline: true, size: "small", placeholder: "\u4EE5 JSON \u683C\u5F0F\u8F93\u5165\u670D\u52A1\u8BF7\u6C42", value: config.requestPayload, onChange: (event) => {
                                    setConfig({ ...config, requestPayload: event.target.value });
                                }, error: requestParseError != undefined }), requestParseError && (_jsx(Typography, { variant: "caption", noWrap: true, color: requestParseError ? "error" : undefined, children: requestParseError }))] }), _jsxs(Stack, { flexGrow: "1", children: [_jsx(Typography, { variant: "caption", noWrap: true, children: "Response" }), _jsx(TextField, { variant: "outlined", className: classes.textarea, multiline: true, size: "small", placeholder: "\u54CD\u5E94", value: state?.value, error: state?.status === "error" })] })] }), _jsxs(Stack, { direction: "row", justifyContent: "flex-end", alignItems: "center", overflow: "hidden", flexGrow: 0, gap: 1.5, children: [statusMessage && (_jsx(Typography, { variant: "caption", noWrap: true, children: statusMessage })), _jsx(Tooltip, { title: config.buttonTooltip, children: _jsx("span", { children: _jsx(Button, { className: classes.button, variant: "contained", disabled: !canCallService, onClick: callServiceClicked, "data-testid": "call-service-button", children: config.buttonText ? config.buttonText : `Call service ${config.serviceName ?? ""}` }) }) })] })] }));
}
