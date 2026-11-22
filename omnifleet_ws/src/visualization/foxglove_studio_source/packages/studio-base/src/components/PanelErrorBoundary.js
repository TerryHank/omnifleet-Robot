import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { Button, Link } from "@mui/material";
import { Component } from "react";
import Stack from "@foxglove/studio-base/components/Stack";
import { reportError } from "@foxglove/studio-base/reportError";
import { AppError } from "@foxglove/studio-base/util/errors";
import ErrorDisplay from "./ErrorDisplay";
export default class PanelErrorBoundary extends Component {
    state = {
        currentError: undefined,
    };
    componentDidCatch(error, errorInfo) {
        reportError(new AppError(error, errorInfo));
        this.setState({ currentError: { error, errorInfo } });
    }
    render() {
        if (this.state.currentError) {
            return (_jsx(ErrorDisplay, { title: "\u6B64\u9762\u677F\u9047\u5230\u610F\u5916\u9519\u8BEF", error: this.state.currentError.error, errorInfo: this.state.currentError.errorInfo, showErrorDetails: this.props.showErrorDetails, hideErrorSourceLocations: this.props.hideErrorSourceLocations, content: _jsxs("p", { children: ["Something went wrong in this panel.", " ", _jsx(Link, { color: "inherit", onClick: () => {
                                this.setState({ currentError: undefined });
                            }, children: "Dismiss this error" }), " ", "to continue using this panel. If the issue persists, try resetting the panel."] }), actions: _jsx(_Fragment, { children: _jsxs(Stack, { direction: "row-reverse", gap: 1, children: [_jsx(Button, { variant: "outlined", color: "secondary", onClick: () => {
                                    this.setState({ currentError: undefined });
                                }, children: "Dismiss" }), _jsx(Button, { variant: "outlined", title: "\u5C06\u9762\u677F\u8BBE\u7F6E\u6062\u590D\u4E3A\u9ED8\u8BA4\u503C", color: "error", onClick: () => {
                                    this.setState({ currentError: undefined });
                                    this.props.onResetPanel();
                                }, children: "Reset Panel" }), _jsx(Button, { variant: "text", title: "\u4ECE\u5E03\u5C40\u4E2D\u5220\u9664\u6B64\u9762\u677F", color: "error", onClick: this.props.onRemovePanel, children: "Remove Panel" })] }) }) }));
        }
        return this.props.children;
    }
}
