import { jsx as _jsx, Fragment as _Fragment, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import ArrowDownIcon from "@mui/icons-material/ArrowDropDown";
import ArrowRightIcon from "@mui/icons-material/ArrowRight";
import CheckIcon from "@mui/icons-material/Check";
import EditIcon from "@mui/icons-material/Edit";
import ErrorIcon from "@mui/icons-material/Error";
import { Button, Divider, IconButton, TextField, Tooltip, Typography } from "@mui/material";
import * as _ from "lodash-es";
import memoizeWeak from "memoize-weak";
import { useCallback, useEffect, useMemo, useRef } from "react";
import { useTranslation } from "react-i18next";
import tinycolor from "tinycolor2";
import { keyframes } from "tss-react";
import { makeStyles } from "tss-react/mui";
import { useImmer } from "use-immer";
import { filterMap } from "@foxglove/den/collection";
import { HighlightedText } from "@foxglove/studio-base/components/HighlightedText";
import Stack from "@foxglove/studio-base/components/Stack";
import { useAppContext } from "@foxglove/studio-base/context/AppContext";
import { FieldEditor } from "./FieldEditor";
import { NodeActionsMenu } from "./NodeActionsMenu";
import { VisibilityToggle } from "./VisibilityToggle";
import { icons } from "./icons";
import { prepareSettingsNodes } from "./utils";
const NODE_HEADER_MIN_HEIGHT = 35;
const useStyles = makeStyles()((theme) => ({
    actionButton: {
        padding: theme.spacing(0.5),
    },
    editNameField: {
        font: "inherit",
        gridColumn: "span 2",
        width: "100%",
        ".MuiInputBase-input": {
            fontSize: "0.75rem",
            padding: theme.spacing(0.75, 1),
        },
    },
    focusedNode: {
        animation: `
      ${keyframes `
      from {
        background-color: ${tinycolor(theme.palette.primary.main).setAlpha(0.3).toRgbString()};
      }
      to {
        background-color: transparent;
      }`}
      0.5s ease-in-out
    `,
    },
    fieldPadding: {
        gridColumn: "span 2",
        height: theme.spacing(0.5),
    },
    iconWrapper: {
        position: "absolute",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        top: "50%",
        left: 0,
        transform: "translate(-97.5%, -50%)",
    },
    nodeHeader: {
        display: "flex",
        gridColumn: "span 2",
        paddingRight: theme.spacing(0.5),
        minHeight: NODE_HEADER_MIN_HEIGHT,
        "@media (pointer: fine)": {
            ".MuiCheckbox-root": {
                visibility: "visible",
            },
            "[data-node-function=edit-label]": {
                visibility: "hidden",
            },
            "&:hover": {
                backgroundColor: theme.palette.action.hover,
                ".MuiCheckbox-root": {
                    visibility: "visible",
                },
                "[data-node-function=edit-label]": {
                    visibility: "visible",
                },
            },
        },
    },
    nodeHeaderVisible: {
        "@media (pointer: fine)": {
            ".MuiCheckbox-root": {
                visibility: "hidden",
            },
            "&:hover": {
                ".MuiCheckbox-root": {
                    visibility: "visible",
                },
            },
        },
    },
    nodeHeaderToggle: {
        display: "grid",
        alignItems: "center",
        gridTemplateColumns: "auto 1fr auto",
        opacity: 0.6,
        position: "relative",
        userSelect: "none",
        width: "100%",
    },
    nodeHeaderToggleHasProperties: {
        cursor: "pointer",
    },
    nodeHeaderToggleVisible: {
        opacity: 1,
    },
    errorTooltip: {
        whiteSpace: "pre-line",
        maxHeight: "15vh",
        overflowY: "auto",
    },
}));
function ExpansionArrow({ expanded }) {
    const { classes } = useStyles();
    const Component = expanded ? ArrowDownIcon : ArrowRightIcon;
    return (_jsx("div", { className: classes.iconWrapper, children: _jsx(Component, {}) }));
}
const makeStablePath = memoizeWeak((path, key) => [...path, key]);
const SelectVisibilityFilterOptions = (t) => [
    { label: t("listAll"), value: "all" },
    { label: t("listVisible"), value: "visible" },
    { label: t("listInvisible"), value: "invisible" },
];
function showVisibleFilter(child) {
    // want to show children with undefined visibility
    return child.visible !== false;
}
function showInvisibleFilter(child) {
    // want to show children with undefined visibility
    return child.visible !== true;
}
const getSelectVisibilityFilterField = (t) => ({
    input: "select",
    label: t("filterList"),
    help: t("filterListHelp"),
    options: SelectVisibilityFilterOptions(t),
});
function NodeEditorComponent(props) {
    const { actionHandler, defaultOpen = true, filter, focusedPath, settings = {} } = props;
    const [state, setState] = useImmer({
        editing: false,
        focusedPath: undefined,
        open: defaultOpen,
        visibilityFilter: "all",
    });
    const { renderSettingsStatusButton } = useAppContext();
    const { t } = useTranslation("settingsEditor");
    const { classes, cx, theme } = useStyles();
    const indent = props.path.length;
    const allowVisibilityToggle = props.settings?.visible != undefined;
    const visible = props.settings?.visible !== false;
    const selectVisibilityFilterEnabled = props.settings?.enableVisibilityFilter === true;
    const selectVisibilityFilter = (action) => {
        if (action.action === "update" && action.payload.input === "select") {
            setState((draft) => {
                draft.visibilityFilter = action.payload.value;
            });
        }
    };
    const toggleVisibility = () => {
        actionHandler({
            action: "update",
            payload: { input: "boolean", path: [...props.path, "visible"], value: !visible },
        });
    };
    const handleNodeAction = (actionId) => {
        actionHandler({ action: "perform-node-action", payload: { id: actionId, path: props.path } });
    };
    const isFocused = _.isEqual(focusedPath, props.path);
    useEffect(() => {
        const isOnFocusedPath = focusedPath != undefined && _.isEqual(props.path, focusedPath.slice(0, props.path.length));
        if (isOnFocusedPath) {
            setState((draft) => {
                draft.open = true;
            });
        }
        if (isFocused) {
            rootRef.current?.scrollIntoView();
        }
    }, [focusedPath, isFocused, props.path, setState]);
    const { fields, children } = settings;
    const hasChildren = children != undefined && Object.keys(children).length > 0;
    const hasProperties = fields != undefined || hasChildren;
    const rootRef = useRef(ReactNull);
    const fieldEditors = filterMap(Object.entries(fields ?? {}), ([key, field]) => {
        return field ? (_jsx(FieldEditor, { field: field, path: makeStablePath(props.path, key), actionHandler: actionHandler }, key)) : undefined;
    });
    const filterFn = state.visibilityFilter === "visible"
        ? showVisibleFilter
        : state.visibilityFilter === "invisible"
            ? showInvisibleFilter
            : undefined;
    const childNodes = filterMap(prepareSettingsNodes(children ?? {}), ([key, child]) => {
        return !filterFn || filterFn(child) ? (_jsx(NodeEditor, { actionHandler: actionHandler, defaultOpen: child.defaultExpansionState === "collapsed" ? false : true, filter: filter, focusedPath: focusedPath, settings: child, path: makeStablePath(props.path, key) }, key)) : undefined;
    });
    const IconComponent = settings.icon ? icons[settings.icon] : undefined;
    const onEditLabel = useCallback((event) => {
        if (settings.renamable === true) {
            actionHandler({
                action: "update",
                payload: { path: [...props.path, "label"], input: "string", value: event.target.value },
            });
        }
    }, [actionHandler, props.path, settings.renamable]);
    const toggleEditing = useCallback(() => {
        setState((draft) => {
            draft.editing = !draft.editing;
        });
    }, [setState]);
    const toggleOpen = useCallback(() => {
        setState((draft) => {
            if (!draft.editing) {
                draft.open = !draft.open;
            }
        });
    }, [setState]);
    const onLabelKeyDown = useCallback((event) => {
        if (event.key === "Enter" || event.key === "Escape") {
            toggleEditing();
        }
    }, [toggleEditing]);
    const [inlineActions, menuActions] = useMemo(() => _.partition(settings.actions, (action) => action.type === "action" && action.display === "inline"), [settings.actions]);
    const statusButton = renderSettingsStatusButton
        ? renderSettingsStatusButton(settings)
        : undefined;
    // Determine the item to render in the icon slot
    // If there's an error we render the error dot, otherwise we render the provided IconComponent
    const iconItem = useMemo(() => {
        if (props.settings?.error) {
            return (_jsx(Tooltip, { arrow: true, title: _jsx(Typography, { variant: "subtitle2", className: classes.errorTooltip, children: props.settings.error }), children: _jsx(ErrorIcon, { fontSize: "small", color: "error", style: {
                        marginRight: theme.spacing(0.5),
                    } }) }));
        }
        if (IconComponent) {
            return (_jsx(IconComponent, { fontSize: "small", color: "inherit", style: {
                    marginRight: theme.spacing(0.5),
                    opacity: 0.8,
                } }));
        }
        return _jsx(_Fragment, {});
    }, [IconComponent, classes.errorTooltip, props.settings?.error, theme]);
    return (_jsxs(_Fragment, { children: [_jsxs("div", { className: cx(classes.nodeHeader, {
                    [classes.focusedNode]: isFocused,
                    [classes.nodeHeaderVisible]: visible,
                }), ref: rootRef, children: [_jsxs("div", { className: cx(classes.nodeHeaderToggle, {
                            [classes.nodeHeaderToggleHasProperties]: hasProperties,
                            [classes.nodeHeaderToggleVisible]: visible,
                        }), style: {
                            marginLeft: theme.spacing(0.75 + 2 * indent),
                        }, onClick: toggleOpen, "data-testid": `settings__nodeHeaderToggle__${props.path.join("-")}`, children: [hasProperties && _jsx(ExpansionArrow, { expanded: state.open }), iconItem, state.editing ? (_jsx(TextField, { className: classes.editNameField, autoFocus: true, variant: "filled", onChange: onEditLabel, value: settings.label, onBlur: toggleEditing, onKeyDown: onLabelKeyDown, onFocus: (event) => {
                                    event.target.select();
                                }, InputProps: {
                                    endAdornment: (_jsx(IconButton, { className: classes.actionButton, title: "\u91CD\u547D\u540D", "data-node-function": "edit-label", color: "primary", onClick: (event) => {
                                            event.stopPropagation();
                                            toggleEditing();
                                        }, children: _jsx(CheckIcon, { fontSize: "small" }) })),
                                } })) : (_jsx(Typography, { noWrap: true, flex: "auto", variant: "subtitle2", fontWeight: indent < 2 ? 600 : 400, color: visible ? "text.primary" : "text.disabled", children: _jsx(HighlightedText, { text: settings.label ?? t("general"), highlight: filter }) }))] }), _jsxs(Stack, { alignItems: "center", direction: "row", children: [settings.renamable === true && !state.editing && (_jsx(IconButton, { className: classes.actionButton, title: "\u91CD\u547D\u540D", "data-node-function": "edit-label", color: "primary", onClick: (event) => {
                                    event.stopPropagation();
                                    toggleEditing();
                                }, children: _jsx(EditIcon, { fontSize: "small" }) })), statusButton
                                ? statusButton
                                : settings.visible != undefined && (_jsx(VisibilityToggle, { size: "small", checked: visible, onChange: toggleVisibility, style: { opacity: allowVisibilityToggle ? 1 : 0 }, disabled: !allowVisibilityToggle })), inlineActions.map((action) => {
                                const Icon = action.icon ? icons[action.icon] : undefined;
                                const handler = () => {
                                    actionHandler({
                                        action: "perform-node-action",
                                        payload: { id: action.id, path: props.path },
                                    });
                                };
                                return Icon ? (_jsx(IconButton, { onClick: handler, title: action.label, className: classes.actionButton, children: _jsx(Icon, { fontSize: "small" }) }, action.id)) : (_jsx(Button, { onClick: handler, size: "small", color: "inherit", className: classes.actionButton, children: action.label }, action.id));
                            }), menuActions.length > 0 && (_jsx(NodeActionsMenu, { actions: menuActions, onSelectAction: handleNodeAction }))] })] }), state.open && fieldEditors.length > 0 && (_jsxs(_Fragment, { children: [_jsx("div", { className: classes.fieldPadding }), fieldEditors, _jsx("div", { className: classes.fieldPadding })] })), state.open && selectVisibilityFilterEnabled && hasChildren && (_jsxs(_Fragment, { children: [_jsx(Stack, { paddingBottom: 0.5, style: { gridColumn: "span 2" } }), _jsx(FieldEditor, { field: { ...getSelectVisibilityFilterField(t), value: state.visibilityFilter }, path: makeStablePath(props.path, "visibilityFilter"), actionHandler: selectVisibilityFilter }, "visibilityFilter")] })), state.open && childNodes, indent === 1 && _jsx(Divider, { style: { gridColumn: "span 2" } })] }));
}
export const NodeEditor = React.memo(NodeEditorComponent);
