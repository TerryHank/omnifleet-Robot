import { Fragment as _Fragment, jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import ICONS from "@foxglove/studio-base/theme/icons";
export function BuiltinIcon(props) {
    if (props.name == undefined) {
        return _jsx(_Fragment, {});
    }
    return ICONS[props.name];
}
