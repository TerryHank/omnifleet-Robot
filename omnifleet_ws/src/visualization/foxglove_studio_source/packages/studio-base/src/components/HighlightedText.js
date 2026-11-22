import { jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import * as _ from "lodash-es";
/**
 * Renders the given text with the span matching highlight wrapped in a
 * <mark> component.
 */
export function HighlightedText({ text, highlight, }) {
    if (!highlight?.trim()) {
        return _jsx("span", { children: text });
    }
    const regex = new RegExp(`(${_.escapeRegExp(highlight)})`, "gi");
    const parts = text.split(regex);
    return (_jsx("span", { children: parts
            .filter((part) => part)
            .map((part, i) => regex.test(part) ? _jsx("mark", { children: part }, i) : _jsx("span", { children: part }, i)) }));
}
