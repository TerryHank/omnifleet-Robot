import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { MenuItem } from "@mui/material";
import { useMemo } from "react";
import { FixedSizeList } from "react-window";
import { makeStyles } from "tss-react/mui";
import { HighlightChars } from "@foxglove/studio-base/components/HighlightChars";
const Constants = Object.freeze({
    LISTBOX_PADDING: 8,
    ROW_HEIGHT: 26,
});
const useStyles = makeStyles()((theme) => ({
    item: {
        padding: 6,
        cursor: "pointer",
        minHeight: "100%",
        lineHeight: "calc(100% - 10px)",
        overflowWrap: "break-word",
        color: theme.palette.text.primary,
        // re-establish the <mark /> styles because the autocomplete is in a Portal
        mark: {
            backgroundColor: "transparent",
            color: theme.palette.info.main,
            fontWeight: 700,
        },
    },
    itemHighlighted: {
        backgroundColor: theme.palette.action.hover,
    },
}));
/**
 * React-window adapter to use a virtualized list as the autocomplete ListboxComponent to support
 * lists with thousands of elements without rendering all of them to the DOM.
 *
 * From the Autocomplete parent it receives a list of children (which must conform to the
 * ListboxAdapterChild type), and props to apply to the outer listbox element.
 */
export const ReactWindowListboxAdapter = React.forwardRef(function ListboxComponent(props, ref) {
    const { children, ...other } = props;
    const { className, ...rest } = other;
    const options = children;
    const longestChild = useMemo(() => options.reduce((prev, item) => {
        if (item[1].item.length > prev.length) {
            return item[1].item;
        }
        return prev;
    }, ""), [options]);
    const totalHeight = 2 * Constants.LISTBOX_PADDING + Constants.ROW_HEIGHT * Math.min(options.length, 16);
    // The hidden div is a trick to cause the parent div to expand to the width of the longest child
    // in the list. Without this, the parent div would have a width of 0 because the FixedSizeList
    // places items using position absolute which means they do not impact the size of their parent.
    return (_jsxs("div", { ref: ref, ...rest, children: [_jsx("div", { style: { visibility: "hidden", height: 0 }, children: longestChild }), _jsx(FixedSizeList, { height: totalHeight, itemCount: options.length, itemData: options, itemSize: Constants.ROW_HEIGHT, className: className, width: "100%", children: FixedSizeListRenderRow })] }));
});
/** Render an individual row for the FixedSizeList */
function FixedSizeListRenderRow(props) {
    // data is the array of all items, index is the index of the current row (item), and style
    // is the position style for the specific item
    const { data, index, style } = props;
    const { classes, cx } = useStyles();
    const dataSet = data[index];
    if (!dataSet) {
        return ReactNull;
    }
    const inlineStyle = {
        ...style,
        top: style.top + Constants.LISTBOX_PADDING,
    };
    const [optProps, item, opt] = dataSet;
    const itemValue = item.item;
    return (_jsx("div", { style: inlineStyle, children: _jsx(MenuItem, { ...optProps, dense: true, component: "span", "data-highlighted": opt.selected, "data-testid": "autocomplete-item", className: cx(classes.item, {
                [classes.itemHighlighted]: opt.selected,
            }), children: _jsx(HighlightChars, { str: itemValue, indices: item.positions }) }) }, itemValue));
}
