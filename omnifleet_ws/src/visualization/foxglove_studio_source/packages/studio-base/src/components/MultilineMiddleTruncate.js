import { jsx as _jsx, Fragment as _Fragment } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import TextMiddleTruncate from "@foxglove/studio-base/components/TextMiddleTruncate";
/**
 * Render multiline text using TextMiddleTruncate for each line.
 */
export function MultilineMiddleTruncate(props) {
    const { text } = props;
    return (_jsx(_Fragment, { children: text.split("\n").map((line) => (_jsx(TextMiddleTruncate, { text: line }, line))) }));
}
