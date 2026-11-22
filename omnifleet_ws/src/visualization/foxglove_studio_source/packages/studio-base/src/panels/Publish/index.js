import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
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
import { Button, inputBaseClasses, TextField, Tooltip, Typography } from "@mui/material";
import { useEffect, useMemo } from "react";
import { makeStyles } from "tss-react/mui";
import { useDebounce } from "use-debounce";
import CommonRosTypes from "@foxglove/rosmsg-msgs-common";
import { useDataSourceInfo } from "@foxglove/studio-base/PanelAPI";
import { useMessagePipeline, } from "@foxglove/studio-base/components/MessagePipeline";
import Panel from "@foxglove/studio-base/components/Panel";
import PanelToolbar from "@foxglove/studio-base/components/PanelToolbar";
import Stack from "@foxglove/studio-base/components/Stack";
import useCallbackWithToast from "@foxglove/studio-base/hooks/useCallbackWithToast";
import usePublisher from "@foxglove/studio-base/hooks/usePublisher";
import { PlayerCapabilities } from "@foxglove/studio-base/players/types";
import { useDefaultPanelTitle } from "@foxglove/studio-base/providers/PanelStateContextProvider";
import { defaultConfig, usePublishPanelSettings } from "./settings";
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
                width: "100%",
                height: "100%",
                textAlign: "left",
                backgroundColor: theme.palette.background.paper,
                overflow: "hidden",
                padding: theme.spacing(1, 0.5),
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
            error = "Message content must be an object, not an array";
        }
        else if (parsedAny == null /* eslint-disable-line no-restricted-syntax */) {
            error = "Message content must be an object, not null";
        }
        else if (typeof parsedAny !== "object") {
            error = `Message content must be an object, not ‘${typeof parsedAny}’`;
        }
        else {
            parsedObject = parsedAny;
        }
    }
    catch (e) {
        error = value.length !== 0 ? e.message : "Enter valid message content as JSON";
    }
    return { error, parsedObject };
}
function selectDataSourceProfile(ctx) {
    return ctx.playerState.profile;
}
function Publish(props) {
    const { saveConfig, config } = props;
    const { topics, datatypes: dataSourceDatatypes, capabilities } = useDataSourceInfo();
    const { classes } = useStyles({ buttonColor: config.buttonColor });
    const [debouncedTopicName] = useDebounce(config.topicName ?? "", 500);
    const dataSourceProfile = useMessagePipeline(selectDataSourceProfile);
    const datatypes = useMemo(() => {
        // Add common ROS datatypes, depending on the data source profile.
        const commonTypes = {
            ros1: CommonRosTypes.ros1,
            ros2: CommonRosTypes.ros2galactic,
        }[dataSourceProfile ?? ""];
        if (commonTypes == undefined) {
            return dataSourceDatatypes;
        }
        // dataSourceDatatypes is added after commonTypes to take precedence (override) any commonTypes of the same name
        return new Map([
            ...Object.entries(commonTypes),
            ...dataSourceDatatypes,
        ]);
    }, [dataSourceProfile, dataSourceDatatypes]);
    const publish = usePublisher({
        name: "Publish",
        topic: debouncedTopicName,
        schemaName: config.datatype,
        datatypes,
    });
    const { error, parsedObject } = useMemo(() => parseInput(config.value ?? ""), [config.value]);
    usePublishPanelSettings(config, saveConfig, topics, datatypes);
    const onPublishClicked = useCallbackWithToast(() => {
        if (config.topicName != undefined && parsedObject != undefined) {
            publish(parsedObject);
        }
        else {
            throw new Error(`called _publish() when input was invalid`);
        }
    }, [config.topicName, parsedObject, publish]);
    const [, setDefaultPanelTitle] = useDefaultPanelTitle();
    useEffect(() => {
        if (config.topicName != undefined && config.topicName.length > 0) {
            setDefaultPanelTitle(`Publish ${config.topicName}`);
        }
        else {
            setDefaultPanelTitle("Publish");
        }
    }, [config.topicName, setDefaultPanelTitle]);
    const canPublish = Boolean(capabilities.includes(PlayerCapabilities.advertise) &&
        config.value &&
        config.topicName &&
        config.datatype &&
        parsedObject != undefined);
    const statusMessage = useMemo(() => {
        if (!capabilities.includes(PlayerCapabilities.advertise)) {
            return "Connect to a data source that supports publishing";
        }
        if (!config.topicName || !config.datatype) {
            return "Configure a topic and message schema in the panel settings";
        }
        return undefined;
    }, [capabilities, config.datatype, config.topicName]);
    return (_jsxs(Stack, { fullHeight: true, children: [_jsx(PanelToolbar, {}), _jsxs(Stack, { flex: "auto", gap: 1, padding: 1.5, position: "relative", children: [config.advancedView && (_jsx(Stack, { flexGrow: "1", children: _jsx(TextField, { variant: "outlined", className: classes.textarea, multiline: true, size: "small", placeholder: "\u4EE5 JSON \u683C\u5F0F\u8F93\u5165\u6D88\u606F\u5185\u5BB9", value: config.value, onChange: (event) => {
                                saveConfig({ value: event.target.value });
                            }, error: error != undefined }) })), _jsxs(Stack, { direction: config.advancedView ? "row" : "column-reverse", justifyContent: config.advancedView ? "flex-end" : "center", alignItems: "center", overflow: "hidden", flexGrow: 0, gap: 1.5, children: [(error != undefined || statusMessage != undefined) && (_jsx(Typography, { variant: "caption", noWrap: true, color: error ? "error" : undefined, children: error ?? statusMessage })), _jsx(Tooltip, { placement: config.advancedView ? "left" : undefined, title: config.buttonTooltip, children: _jsx("span", { children: _jsx(Button, { className: classes.button, variant: "contained", disabled: !canPublish, onClick: onPublishClicked, children: config.buttonText }) }) })] })] })] }));
}
export default Panel(Object.assign(React.memo(Publish), {
    panelType: "Publish",
    defaultConfig,
}));
