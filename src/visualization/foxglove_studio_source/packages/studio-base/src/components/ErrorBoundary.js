import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { Link, Button, Typography } from "@mui/material";
import { Component } from "react";
import Stack from "@foxglove/studio-base/components/Stack";
import { reportError } from "@foxglove/studio-base/reportError";
import { AppError } from "@foxglove/studio-base/util/errors";
import ErrorDisplay from "./ErrorDisplay";
export default class ErrorBoundary extends Component {
    state = {
        currentError: undefined,
    };
    componentDidCatch(error, errorInfo) {
        reportError(new AppError(error, errorInfo));
        this.setState({ currentError: { error, errorInfo } });
    }
    render() {
        if (this.state.currentError) {
            const actions = this.props.actions ?? (_jsx(Stack, { fullHeight: true, flex: "auto", alignItems: "flex-end", justifyContent: "flex-end", direction: "row", children: _jsx(Button, { variant: "outlined", color: "secondary", onClick: () => {
                        this.setState({ currentError: undefined });
                    }, children: "Dismiss" }) }));
            return (_jsx(ErrorDisplay, { showErrorDetails: this.props.showErrorDetails, hideErrorSourceLocations: this.props.hideErrorSourceLocations, error: this.state.currentError.error, errorInfo: this.state.currentError.errorInfo, content: _jsxs(Typography, { children: ["Something went wrong.", " ", _jsx(Link, { color: "inherit", onClick: () => {
                                this.setState({ currentError: undefined });
                            }, children: "Dismiss this error" }), " ", "to continue using the app. If the issue persists, try restarting the app."] }), actions: actions }));
        }
        return this.props.children;
    }
}
