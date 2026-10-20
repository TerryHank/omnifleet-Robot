import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import DiffIcon from "@mui/icons-material/Difference";
import DiffOutlinedIcon from "@mui/icons-material/DifferenceOutlined";
import UnfoldLessIcon from "@mui/icons-material/UnfoldLess";
import UnfoldMoreIcon from "@mui/icons-material/UnfoldMore";
import { IconButton, MenuItem, Select } from "@mui/material";
import { makeStyles } from "tss-react/mui";
import MessagePathInput from "@foxglove/studio-base/components/MessagePathSyntax/MessagePathInput";
import PanelToolbar from "@foxglove/studio-base/components/PanelToolbar";
import Stack from "@foxglove/studio-base/components/Stack";
import { Constants } from "./types";
const useStyles = makeStyles()((theme) => ({
    toolbar: {
        paddingBlock: 0,
        gap: theme.spacing(0.25),
    },
    iconButton: {
        padding: theme.spacing(0.25),
        "&.Mui-selected": {
            color: theme.palette.primary.main,
            backgroundColor: theme.palette.action.selected,
        },
    },
    diffOptions: {
        borderTop: `1px solid ${theme.palette.background.default}`,
        backgroundColor: theme.palette.background.paper,
        padding: theme.spacing(0.25, 0.75),
        paddingInlineEnd: theme.spacing(6.75),
        gap: theme.spacing(0.25),
        display: "flex",
    },
}));
function ToolbarComponent(props) {
    const { canExpandAll, diffEnabled, diffMethod, diffTopicPath, onDiffTopicPathChange, onToggleDiff, onToggleExpandAll, onTopicPathChange, saveConfig, topic, topicPath, } = props;
    const { classes, cx } = useStyles();
    return (_jsxs(_Fragment, { children: [_jsxs(PanelToolbar, { className: classes.toolbar, children: [_jsx(IconButton, { className: cx(classes.iconButton, { "Mui-selected": diffEnabled }), title: "\u5207\u6362\u5DEE\u5F02\u6A21\u5F0F", onClick: onToggleDiff, color: diffEnabled ? "default" : "inherit", size: "small", children: diffEnabled ? _jsx(DiffIcon, { fontSize: "small" }) : _jsx(DiffOutlinedIcon, { fontSize: "small" }) }), _jsx(IconButton, { className: classes.iconButton, title: canExpandAll ? "Expand all" : "Collapse all", onClick: onToggleExpandAll, "data-testid": "expand-all", size: "small", children: canExpandAll ? _jsx(UnfoldMoreIcon, { fontSize: "small" }) : _jsx(UnfoldLessIcon, { fontSize: "small" }) }), _jsx(Stack, { fullWidth: true, paddingLeft: 0.25, children: _jsx(MessagePathInput, { index: 0, path: topicPath, onChange: onTopicPathChange, inputStyle: { height: 20 } }) })] }), diffEnabled && (_jsxs("div", { className: classes.diffOptions, children: [_jsxs(Select, { variant: "filled", size: "small", title: "\u5DEE\u5F02\u6BD4\u8F83\u65B9\u5F0F", value: diffMethod, MenuProps: { MenuListProps: { dense: true } }, onChange: (event) => {
                            saveConfig({
                                diffMethod: event.target.value,
                            });
                        }, children: [_jsx(MenuItem, { value: Constants.PREV_MSG_METHOD, children: Constants.PREV_MSG_METHOD }), _jsx(MenuItem, { value: Constants.CUSTOM_METHOD, children: "custom" })] }), diffMethod === Constants.CUSTOM_METHOD && (_jsx(MessagePathInput, { index: 1, path: diffTopicPath, onChange: onDiffTopicPathChange, ...(topic ? { prioritizedDatatype: topic.schemaName } : {}) }))] }))] }));
}
export const Toolbar = React.memo(ToolbarComponent);
