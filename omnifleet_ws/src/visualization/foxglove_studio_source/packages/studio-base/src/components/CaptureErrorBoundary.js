import { Fragment as _Fragment, jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { Component } from "react";
/** An error boundary that calls an onError function when it captures an error */
export class CaptureErrorBoundary extends Component {
    state = {
        hadError: false,
    };
    componentDidCatch(error) {
        this.setState({ hadError: true });
        this.props.onError(error);
    }
    render() {
        // Avoid rendering children since the children are what caused the error
        if (this.state.hadError) {
            return _jsx(_Fragment, {});
        }
        return this.props.children;
    }
}
