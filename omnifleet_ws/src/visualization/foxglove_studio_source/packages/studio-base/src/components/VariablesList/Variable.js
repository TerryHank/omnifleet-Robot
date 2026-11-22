import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import ErrorIcon from "@mui/icons-material/Error";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import { Divider, IconButton, Menu, MenuItem, ListItem, ListItemButton, ListItemText, Typography, Tooltip, InputBase, } from "@mui/material";
import * as _ from "lodash-es";
import { useMemo, useCallback, useState, useRef } from "react";
import { makeStyles } from "tss-react/mui";
import CopyButton from "@foxglove/studio-base/components/CopyButton";
import JsonInput from "@foxglove/studio-base/components/JsonInput";
import Stack from "@foxglove/studio-base/components/Stack";
import { useAnalytics } from "@foxglove/studio-base/context/AnalyticsContext";
import useGlobalVariables from "@foxglove/studio-base/hooks/useGlobalVariables";
import { AppEvent } from "@foxglove/studio-base/services/IAnalytics";
const useStyles = makeStyles()((theme, _params, classes) => ({
    root: {
        "@media (pointer: fine)": {
            [`&:not(:hover) .${classes.copyButton}`]: {
                visibility: "hidden",
            },
        },
    },
    copyButton: {
        top: 0,
        right: 0,
        zIndex: theme.zIndex.mobileStepper,
        "&.MuiButton-root": {
            position: "absolute",
            paddingLeft: theme.spacing(1),
            paddingRight: theme.spacing(1),
            margin: theme.spacing(0.75),
            minWidth: "auto",
        },
    },
    input: {
        font: "inherit",
        flex: "auto",
        ".MuiInputBase-input": {
            padding: 0,
        },
        "&.Mui-error": {
            color: theme.palette.error.main,
        },
    },
    edgeEnd: {
        marginRight: theme.spacing(-1.625),
    },
    editorWrapper: {
        position: "relative",
        backgroundColor: theme.palette.grey[50],
    },
    listItemButton: {
        "&:focus-within": {
            backgroundColor: "transparent",
        },
        "&.Mui-selected": {
            color: theme.palette.primary.main,
            transition: `background-color 300ms ease-in-out`,
        },
    },
    listItemText: {
        marginTop: theme.spacing(0.125),
        marginBottom: theme.spacing(0.125),
    },
}));
const changeGlobalKey = (newKey, oldKey, globalVariables, idx, overwriteGlobalVariables) => {
    const keys = Object.keys(globalVariables);
    overwriteGlobalVariables({
        ..._.pick(globalVariables, keys.slice(0, idx)),
        [newKey]: globalVariables[oldKey],
        ..._.pick(globalVariables, keys.slice(idx + 1)),
    });
};
export default function Variable(props) {
    const { name, selected = false, index } = props;
    const { classes } = useStyles();
    // When editing the variable name, the new name might collide with an existing variable name
    // If the name matches an existing name, we set the edited name and show an error to the user
    // indicating there is a name conflict. The user must resolve the name conflict or their edited
    // name will be reset on blur.
    const [editedName, setEditedName] = useState();
    const [expanded, setExpanded] = useState(true);
    const [anchorEl, setAnchorEl] = React.useState(undefined);
    const [copied, setCopied] = useState(false);
    const menuOpen = Boolean(anchorEl);
    const { globalVariables, setGlobalVariables, overwriteGlobalVariables } = useGlobalVariables();
    const handleClick = (event) => {
        setAnchorEl(event.currentTarget);
    };
    const handleClose = () => {
        setAnchorEl(undefined);
    };
    const analytics = useAnalytics();
    const deleteVariable = useCallback(() => {
        setGlobalVariables({ [name]: undefined });
        void analytics.logEvent(AppEvent.VARIABLE_DELETE);
        handleClose();
    }, [analytics, name, setGlobalVariables]);
    const value = useMemo(() => globalVariables[name], [globalVariables, name]);
    const onChangeValue = useCallback((newVal) => {
        setGlobalVariables({ [name]: newVal });
        setCopied(false);
    }, [name, setGlobalVariables]);
    const onBlur = () => {
        if (editedName != undefined &&
            globalVariables[editedName] == undefined &&
            name !== editedName) {
            changeGlobalKey(editedName, name, globalVariables, index, overwriteGlobalVariables);
        }
        setEditedName(undefined);
    };
    const rootRef = useRef(ReactNull);
    const activeElementIsChild = rootRef.current?.contains(document.activeElement) === true;
    const isSelected = selected && !activeElementIsChild;
    const isDuplicate = editedName != undefined && editedName !== name && globalVariables[editedName] != undefined;
    const getText = useCallback(() => JSON.stringify(value, undefined, 2) ?? "", [value]);
    return (_jsxs(Stack, { className: classes.root, ref: rootRef, children: [_jsx(ListItem, { dense: true, disablePadding: true, secondaryAction: _jsxs(Stack, { className: classes.edgeEnd, direction: "row", alignItems: "center", gap: 0.25, children: [_jsx(IconButton, { size: "small", id: "variable-action-button", "data-testid": "variable-action-button", "aria-controls": expanded ? "variable-action-menu" : undefined, "aria-haspopup": "true", "aria-expanded": expanded ? "true" : undefined, onClick: handleClick, children: _jsx(MoreVertIcon, { fontSize: "small" }) }), _jsx(Menu, { id: "variable-action-menu", anchorEl: anchorEl, open: menuOpen, onClose: handleClose, MenuListProps: {
                                "aria-labelledby": "variable-action-button",
                                dense: true,
                            }, children: _jsx(MenuItem, { onClick: deleteVariable, children: _jsx(Typography, { color: "error.main", variant: "inherit", children: "Delete variable" }) }) })] }), children: _jsx(ListItemButton, { className: classes.listItemButton, selected: isSelected, onClick: () => {
                        setExpanded(!expanded);
                    }, children: _jsx(ListItemText, { className: classes.listItemText, primary: _jsxs(Stack, { direction: "row", alignItems: "center", style: { marginLeft: -12 }, children: [_jsx(ArrowDropDownIcon, { style: { transform: !expanded ? "rotate(-90deg)" : undefined } }), _jsx(InputBase, { className: classes.input, autoFocus: name === "", error: isDuplicate, value: editedName ?? name, placeholder: "variable_name", "data-testid": `global-variable-key-input-${name}`, onClick: (e) => {
                                        e.stopPropagation();
                                    }, onFocus: () => {
                                        if (editedName === "") {
                                            setExpanded(true);
                                        }
                                    }, onChange: (event) => {
                                        setEditedName(event.target.value);
                                    }, onBlur: onBlur, endAdornment: isDuplicate && (_jsx(Tooltip, { arrow: true, title: "A variable with this name already exists. Please select a unique variable name to save changes.", children: _jsx(ErrorIcon, { className: classes.edgeEnd, fontSize: "small", color: "error" }) })) })] }), primaryTypographyProps: {
                            component: "div",
                            fontWeight: 600,
                            variant: "body2",
                        } }) }) }), expanded && (_jsxs("div", { className: classes.editorWrapper, children: [_jsx(Divider, {}), _jsx(CopyButton, { className: classes.copyButton, size: "small", color: copied ? "primary" : "inherit", getText: getText, children: copied ? "Copied" : "Copy" }), _jsx(JsonInput, { value: value, onChange: onChangeValue })] })), _jsx(Divider, {})] }));
}
