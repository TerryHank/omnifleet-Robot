import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import AddIcon from "@mui/icons-material/Add";
import RemoveIcon from "@mui/icons-material/Remove";
import { Alert, Button, ButtonGroup, CircularProgress, Dialog, DialogActions, DialogContent, DialogTitle, FormControl, FormLabel, IconButton, TextField, ToggleButton, ToggleButtonGroup, Typography, } from "@mui/material";
import * as _ from "lodash-es";
import { useCallback } from "react";
import { useAsyncFn } from "react-use";
import { keyframes } from "tss-react";
import { makeStyles } from "tss-react/mui";
import { useImmer } from "use-immer";
import Log from "@foxglove/log";
import { toDate, toNanoSec } from "@foxglove/rostime";
import { useMessagePipeline, } from "@foxglove/studio-base/components/MessagePipeline";
import Stack from "@foxglove/studio-base/components/Stack";
import { useAppContext } from "@foxglove/studio-base/context/AppContext";
import { useEvents } from "@foxglove/studio-base/context/EventsContext";
import { useAppTimeFormat } from "@foxglove/studio-base/hooks";
const log = Log.getLogger(__filename);
const fadeInAnimation = keyframes `
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
`;
const useStyles = makeStyles()((theme, _params, classes) => ({
    grid: {
        alignItems: "center",
        display: "grid",
        gridTemplateColumns: "1fr 1fr auto",
        gap: theme.spacing(1),
        overflow: "auto",
        alignContent: "flex-start",
    },
    row: {
        animation: `${fadeInAnimation} 0.2s ease-in-out`,
        display: "contents",
    },
    toggleButton: {
        border: "none",
        lineHeight: 1,
    },
    toggleButtonGroup: {
        marginRight: theme.spacing(-0.5),
        gap: theme.spacing(0.25),
        [`.${classes.toggleButton}`]: {
            borderRadius: `${theme.shape.borderRadius}px !important`,
            marginLeft: "0px !important",
            borderLeft: "none !important",
        },
    },
}));
const selectCurrentTime = (ctx) => ctx.playerState.activeData?.currentTime;
const selectRefreshEvents = (store) => store.refreshEvents;
const selectDeviceId = (store) => store.deviceId;
export function CreateEventDialog(props) {
    const { onClose } = props;
    const { classes } = useStyles();
    const refreshEvents = useEvents(selectRefreshEvents);
    const currentTime = useMessagePipeline(selectCurrentTime);
    const [event, setEvent] = useImmer({
        startTime: currentTime ? toDate(currentTime) : undefined,
        duration: 0,
        durationUnit: "sec",
        metadataEntries: [{ key: "", value: "" }],
    });
    const updateMetadata = useCallback((index, updateType, value) => {
        setEvent((draft) => {
            const keyval = draft.metadataEntries[index];
            if (keyval) {
                keyval[updateType] = value;
                // Automatically add new row if we're at the end and have both key and value.
                if (index === draft.metadataEntries.length - 1 &&
                    keyval.key.length > 0 &&
                    keyval.value.length > 0) {
                    draft.metadataEntries.push({ key: "", value: "" });
                }
            }
        });
    }, [setEvent]);
    const { formatTime } = useAppTimeFormat();
    const { createEvent: appModuleCreateEvent } = useAppContext();
    const countedMetadata = _.countBy(event.metadataEntries, (kv) => kv.key);
    const duplicateKey = Object.entries(countedMetadata).find(([key, count]) => key.length > 0 && count > 1);
    const canSubmit = event.startTime != undefined && event.duration != undefined && !duplicateKey;
    const deviceId = useEvents(selectDeviceId);
    const [createdEvent, createEvent] = useAsyncFn(async () => {
        if (event.startTime == undefined || event.duration == undefined || deviceId == undefined) {
            return;
        }
        const filteredMeta = event.metadataEntries.filter((entry) => entry.key.length > 0 && entry.value.length > 0);
        const keyedMetadata = Object.fromEntries(filteredMeta.map((entry) => [entry.key.trim(), entry.value.trim()]));
        await appModuleCreateEvent?.({
            deviceId,
            timestamp: event.startTime.toISOString(),
            durationNanos: toNanoSec(event.durationUnit === "sec"
                ? { sec: event.duration, nsec: 0 }
                : { sec: 0, nsec: event.duration }).toString(),
            metadata: keyedMetadata,
        });
        onClose();
        refreshEvents();
    }, [appModuleCreateEvent, deviceId, event, onClose, refreshEvents]);
    const onMetaDataKeyDown = useCallback((keyboardEvent) => {
        if (keyboardEvent.key === "Enter") {
            createEvent().catch((error) => {
                log.error(error);
            });
        }
    }, [createEvent]);
    const addRow = useCallback((index) => {
        setEvent((draft) => {
            draft.metadataEntries.splice(index + 1, 0, { key: "", value: "" });
        });
    }, [setEvent]);
    const removeRow = useCallback((index) => {
        setEvent((draft) => {
            if (draft.metadataEntries.length > 1) {
                draft.metadataEntries.splice(index, 1);
            }
        });
    }, [setEvent]);
    const formattedStartTime = currentTime ? formatTime(currentTime) : "-";
    return (_jsxs(Dialog, { open: true, onClose: onClose, fullWidth: true, maxWidth: "sm", children: [_jsx(DialogTitle, { children: "Create event" }), _jsxs(DialogContent, { children: [_jsxs("div", { className: classes.grid, children: [_jsxs(FormControl, { children: [_jsx(FormLabel, { children: "Start Time" }), _jsx(Typography, { paddingY: 1, children: formattedStartTime })] }), _jsx(TextField, { value: event.duration ?? "", fullWidth: true, label: "\u6301\u7EED\u65F6\u95F4", onChange: (ev) => {
                                    const duration = Number(ev.currentTarget.value);
                                    setEvent((oldEvent) => ({
                                        ...oldEvent,
                                        duration: duration > 0 ? duration : undefined,
                                    }));
                                }, type: "number", InputProps: {
                                    endAdornment: (_jsxs(ToggleButtonGroup, { className: classes.toggleButtonGroup, size: "small", exclusive: true, value: event.durationUnit, onChange: (_ev, durationUnit) => {
                                            if (event.durationUnit !== durationUnit) {
                                                setEvent((old) => ({ ...old, durationUnit }));
                                            }
                                        }, children: [_jsx(ToggleButton, { className: classes.toggleButton, tabIndex: -1, value: "sec", children: "sec" }), _jsx(ToggleButton, { className: classes.toggleButton, tabIndex: -1, value: "nsec", children: "nsec" })] })),
                                } }), _jsxs(ButtonGroup, { style: { visibility: "hidden" }, children: [_jsx(IconButton, { tabIndex: -1, "data-testid": "add", children: _jsx(AddIcon, {}) }), _jsx(IconButton, { tabIndex: -1, children: _jsx(AddIcon, {}) })] })] }), _jsxs("div", { children: [_jsx(FormLabel, { children: "Metadata" }), _jsx("div", { className: classes.grid, children: event.metadataEntries.map(({ key, value }, index) => {
                                    const hasDuplicate = ((key.length > 0 ? countedMetadata[key] : undefined) ?? 0) > 1;
                                    return (_jsxs("div", { className: classes.row, children: [_jsx(TextField, { fullWidth: true, value: key, autoFocus: index === 0, placeholder: "Key (string)", error: hasDuplicate, onKeyDown: onMetaDataKeyDown, onChange: (evt) => {
                                                    updateMetadata(index, "key", evt.currentTarget.value);
                                                } }), _jsx(TextField, { fullWidth: true, value: value, placeholder: "Value (string)", error: hasDuplicate, onKeyDown: onMetaDataKeyDown, onChange: (evt) => {
                                                    updateMetadata(index, "value", evt.currentTarget.value);
                                                } }), _jsxs(ButtonGroup, { children: [_jsx(IconButton, { tabIndex: -1, onClick: () => {
                                                            addRow(index);
                                                        }, children: _jsx(AddIcon, {}) }), _jsx(IconButton, { tabIndex: -1, onClick: () => {
                                                            removeRow(index);
                                                        }, style: {
                                                            visibility: event.metadataEntries.length > 1 ? "visible" : "hidden",
                                                        }, children: _jsx(RemoveIcon, {}) })] })] }, index));
                                }) })] })] }), duplicateKey && (_jsx(Stack, { paddingX: 3, children: _jsxs(Alert, { severity: "error", children: ["Duplicate key ", duplicateKey[0]] }) })), createdEvent.error?.message && (_jsx(Stack, { paddingX: 3, children: _jsx(Alert, { severity: "error", children: createdEvent.error.message }) })), _jsxs(DialogActions, { children: [_jsx(Button, { variant: "outlined", onClick: onClose, children: "Cancel" }), _jsxs(Button, { variant: "contained", onClick: createEvent, disabled: !canSubmit || createdEvent.loading, children: [createdEvent.loading && (_jsx(CircularProgress, { color: "inherit", size: "1rem", style: { marginRight: "0.5rem" } })), "Create Event"] })] })] }));
}
