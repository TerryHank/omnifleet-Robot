import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { Alert, Link, Tab, Tabs, Typography, useMediaQuery, useTheme } from "@mui/material";
import { useState, useMemo, useCallback, useLayoutEffect } from "react";
import { makeStyles } from "tss-react/mui";
import { BuiltinIcon } from "@foxglove/studio-base/components/BuiltinIcon";
import Stack from "@foxglove/studio-base/components/Stack";
import { useAnalytics } from "@foxglove/studio-base/context/AnalyticsContext";
import { usePlayerSelection } from "@foxglove/studio-base/context/PlayerSelectionContext";
import { useWorkspaceStore, } from "@foxglove/studio-base/context/Workspace/WorkspaceContext";
import { useWorkspaceActions } from "@foxglove/studio-base/context/Workspace/useWorkspaceActions";
import { AppEvent } from "@foxglove/studio-base/services/IAnalytics";
import { FormField } from "./FormField";
import View from "./View";
const useStyles = makeStyles()((theme) => ({
    grid: {
        padding: theme.spacing(4, 4, 0),
        columnGap: theme.spacing(4),
        rowGap: theme.spacing(2),
        [theme.breakpoints.up("md")]: {
            overflow: "hidden",
            display: "grid",
            padding: theme.spacing(4, 4, 0, 4),
            gridTemplateAreas: `
        "header header"
        "sidebar form"
      `,
            gridTemplateColumns: "240px 1fr",
            gridTemplateRows: "auto auto",
        },
    },
    header: {
        gridArea: "header",
    },
    form: {
        gridArea: "form",
        overflowY: "auto",
    },
    formInner: {
        [theme.breakpoints.up("md")]: {
            height: theme.spacing(43), // this is aproximately the height of the tallest form
        },
    },
    sidebar: {
        gridArea: "sidebar",
        overflowY: "auto",
    },
    tab: {
        "> svg:not(.MuiSvgIcon-root)": {
            display: "flex",
            flex: "none",
            color: theme.palette.primary.main,
            marginRight: theme.spacing(1.5),
        },
        [theme.breakpoints.up("md")]: {
            textAlign: "right",
            flexDirection: "row",
            justifyContent: "flex-start",
            alignItems: "center",
            minHeight: "auto",
            paddingTop: theme.spacing(1.5),
            paddingBottom: theme.spacing(1.5),
        },
    },
    indicator: {
        transition: theme.transitions.create("inset"),
        [theme.breakpoints.up("md")]: {
            right: 0,
            width: "100%",
            backgroundColor: theme.palette.action.hover,
            borderRadius: theme.shape.borderRadius,
        },
    },
}));
const selectDataSourceDialog = (store) => store.dialogs.dataSource;
export default function Connection() {
    const { classes } = useStyles();
    const theme = useTheme();
    const mdUp = useMediaQuery(theme.breakpoints.up("md"));
    const { activeDataSource } = useWorkspaceStore(selectDataSourceDialog);
    const { dialogActions } = useWorkspaceActions();
    const { availableSources, selectSource } = usePlayerSelection();
    const analytics = useAnalytics();
    // connectionSources is the list of availableSources supporting "connections"
    const connectionSources = useMemo(() => {
        return availableSources.filter((source) => {
            return source.type === "connection" && source.hidden !== true;
        });
    }, [availableSources]);
    // List enabled sources before disabled sources so the default selected item is an available source
    const enabledSourcesFirst = useMemo(() => {
        const enabledSources = connectionSources.filter((source) => source.disabledReason == undefined);
        const disabledSources = connectionSources.filter((source) => source.disabledReason);
        return [...enabledSources, ...disabledSources];
    }, [connectionSources]);
    const [selectedConnectionIdx, setSelectedConnectionIdx] = useState(() => {
        const foundIdx = connectionSources.findIndex((source) => source === activeDataSource);
        const selectedIdx = foundIdx < 0 ? 0 : foundIdx;
        void analytics.logEvent(AppEvent.DIALOG_SELECT_VIEW, {
            type: "live",
            data: enabledSourcesFirst[selectedIdx]?.id,
        });
        return selectedIdx;
    });
    const selectedSource = useMemo(() => enabledSourcesFirst[selectedConnectionIdx], [enabledSourcesFirst, selectedConnectionIdx]);
    const [fieldErrors, setFieldErrors] = useState(new Map());
    const [fieldValues, setFieldValues] = useState({});
    useLayoutEffect(() => {
        const connectionIdx = connectionSources.findIndex((source) => source === activeDataSource);
        if (connectionIdx >= 0) {
            setSelectedConnectionIdx(connectionIdx);
        }
    }, [activeDataSource, connectionSources]);
    // clear field values when the user changes the source tab
    useLayoutEffect(() => {
        const defaultFieldValues = {};
        for (const field of selectedSource?.formConfig?.fields ?? []) {
            if (field.defaultValue != undefined) {
                defaultFieldValues[field.id] = field.defaultValue;
            }
        }
        setFieldValues(defaultFieldValues);
    }, [selectedSource]);
    const onOpen = useCallback(() => {
        if (!selectedSource) {
            return;
        }
        selectSource(selectedSource.id, { type: "connection", params: fieldValues });
        void analytics.logEvent(AppEvent.DIALOG_CLOSE, { activeDataSource });
        dialogActions.dataSource.close();
    }, [
        selectedSource,
        selectSource,
        fieldValues,
        analytics,
        activeDataSource,
        dialogActions.dataSource,
    ]);
    const disableOpen = selectedSource?.disabledReason != undefined || fieldErrors.size > 0;
    const onSubmit = useCallback((event) => {
        event.preventDefault();
        if (!disableOpen) {
            onOpen();
        }
    }, [disableOpen, onOpen]);
    return (_jsx(View, { onOpen: disableOpen ? undefined : onOpen, children: _jsxs(Stack, { className: classes.grid, "data-testid": "OpenConnection", children: [_jsx("header", { className: classes.header, children: _jsx(Typography, { variant: "h3", fontWeight: 600, gutterBottom: true, children: "Open a new connection" }) }), _jsx("div", { className: classes.sidebar, children: _jsx(Tabs, { classes: { indicator: classes.indicator }, variant: "scrollable", textColor: "inherit", orientation: mdUp ? "vertical" : "horizontal", onChange: (_event, newValue) => {
                            setSelectedConnectionIdx(newValue);
                            void analytics.logEvent(AppEvent.DIALOG_SELECT_VIEW, {
                                type: "live",
                                data: enabledSourcesFirst[newValue]?.id,
                            });
                        }, value: selectedConnectionIdx, children: enabledSourcesFirst.map((source, idx) => {
                            const { id, iconName, displayName } = source;
                            return (_jsx(Tab, { value: idx, icon: mdUp ? _jsx(BuiltinIcon, { name: iconName ?? "Flow" }) : undefined, label: displayName, className: classes.tab }, id));
                        }) }) }), _jsx(Stack, { className: classes.form, flex: "1 0", children: _jsx("form", { onSubmit: onSubmit, children: _jsxs(Stack, { className: classes.formInner, gap: 2, children: [selectedSource?.disabledReason == undefined &&
                                    selectedSource?.warning != undefined && (_jsx(Alert, { severity: "warning", children: selectedSource.warning })), selectedSource?.disabledReason != undefined && (_jsx(Alert, { severity: "warning", children: selectedSource.disabledReason })), selectedSource?.description && _jsx(Typography, { children: selectedSource.description }), selectedSource?.formConfig != undefined && (_jsx(Stack, { flexGrow: 1, justifyContent: "space-between", children: _jsx(Stack, { gap: 2, children: selectedSource.formConfig.fields.map((field) => (_jsx(FormField, { field: field, disabled: selectedSource.disabledReason != undefined, onError: (err) => {
                                                setFieldErrors((existing) => {
                                                    existing.set(field.id, err);
                                                    return new Map(existing);
                                                });
                                            }, onChange: (newValue) => {
                                                setFieldErrors((existing) => {
                                                    existing.delete(field.id);
                                                    return new Map(existing);
                                                });
                                                setFieldValues((existing) => {
                                                    return {
                                                        ...existing,
                                                        [field.id]: newValue,
                                                    };
                                                });
                                            } }, field.id))) }) })), _jsx(Stack, { direction: "row", gap: 1, children: (selectedSource?.docsLinks ?? []).map((item) => (_jsx(Link, { color: "primary", href: item.url, target: "_blank", rel: "noreferrer", children: item.label ? `View docs for ${item.label}` : "View docs" }, item.url))) })] }) }) }, selectedSource?.id)] }) }));
}
