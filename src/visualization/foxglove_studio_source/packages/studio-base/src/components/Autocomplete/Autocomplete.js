import { jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
//
// This file incorporates work covered by the following copyright and
// permission notice:
//
//   Copyright 2018-2021 Cruise LLC
//
//   This source code is licensed under the Apache License, Version 2.0,
//   found at http://www.apache.org/licenses/LICENSE-2.0
//   You may not use this file except in compliance with the License.
import { Autocomplete as MuiAutocomplete, Popper, TextField, } from "@mui/material";
import { Fzf } from "fzf";
import * as React from "react";
import { useCallback, useImperativeHandle, useMemo, useRef, useState, } from "react";
import { makeStyles } from "tss-react/mui";
import { ReactWindowListboxAdapter } from "./ReactWindowListboxAdapter";
const MAX_FZF_MATCHES = 200;
// Above this number of items we fall back to the faster fuzzy find algorithm.
const FAST_FIND_ITEM_CUTOFF = 1000;
const useStyles = makeStyles()((theme) => ({
    inputError: {
        input: {
            color: theme.palette.error.main,
        },
    },
}));
const EMPTY_SET = new Set();
function itemToFzfResult(item) {
    return {
        item,
        score: 0,
        positions: EMPTY_SET,
        start: 0,
        end: 0,
    };
}
// We use fzf to filter the input items to make autocompleteItems so we don't need the
// MuiAutocomplete to also filter the items. Using a passthrough function for filterOptions
// disables the internal filtering of MuiAutocomplete
//
// https://mui.com/material-ui/react-autocomplete/#search-as-you-type
const filterOptions = (options) => options;
const getOptionLabel = (item) => typeof item === "string" ? item : item.item;
// The builtin Popper in MuiAutocomplete uses the width hint from the parent Autocomplete to set
// the width. We want to set the minWidth to allow the popper to grow wider than the input field width,
// so we can show long topic paths and autocomplete entries.
const CustomPopper = function (props) {
    const width = props.style?.width ?? 0;
    return _jsx(Popper, { ...props, style: { minWidth: width }, placement: "bottom-start" });
};
/**
 * <Autocomplete> is a Studio-specific wrapper of MUI autocomplete with support
 * for things like multiple autocompletes that seamlessly transition into each
 * other, e.g. when building more complex strings like in the Plot panel.
 */
export const Autocomplete = React.forwardRef(function Autocomplete(props, ref) {
    const inputRef = useRef(ReactNull);
    const { classes, cx } = useStyles();
    const [stateValue, setValue] = useState(undefined);
    const { className, value = stateValue, disabled, filterText = value ?? "", items, onBlur: onBlurCallback, onChange: onChangeCallback, onSelect: onSelectCallback, placeholder, readOnly, selectOnFocus, sortWhenFiltering = true, variant = "filled", } = props;
    const fzfUnfiltered = useMemo(() => {
        return items.map((item) => itemToFzfResult(item));
    }, [items]);
    const fzf = useMemo(() => {
        return new Fzf(items, {
            // v1 algorithm is significantly faster on long lists of items.
            fuzzy: items.length > FAST_FIND_ITEM_CUTOFF ? "v1" : "v2",
            sort: sortWhenFiltering,
            limit: MAX_FZF_MATCHES,
        });
    }, [items, sortWhenFiltering]);
    const autocompleteItems = useMemo(() => {
        return filterText ? fzf.find(filterText) : fzfUnfiltered;
    }, [filterText, fzf, fzfUnfiltered]);
    const hasError = props.hasError ?? (autocompleteItems.length === 0 && value?.length !== 0);
    const setSelectionRange = useCallback((selectionStart, selectionEnd) => {
        inputRef.current?.focus();
        inputRef.current?.setSelectionRange(selectionStart, selectionEnd);
    }, []);
    const focus = useCallback(() => {
        inputRef.current?.focus();
    }, []);
    const blur = useCallback(() => {
        inputRef.current?.blur();
        onBlurCallback?.();
    }, [onBlurCallback]);
    // Give callers an opportunity to control autocomplete
    useImperativeHandle(ref, () => ({ setSelectionRange, focus, blur }), [
        setSelectionRange,
        focus,
        blur,
    ]);
    const onChange = useCallback((_event, newValue) => {
        if (onChangeCallback) {
            if (_event) {
                onChangeCallback(_event, newValue);
            }
        }
        else {
            setValue(newValue);
        }
    }, [onChangeCallback]);
    // To allow multiple completions in sequence, it's up to the parent component
    // to manually blur the input to finish a completion.
    const onSelect = useCallback((_event, selectedValue) => {
        if (selectedValue != undefined && typeof selectedValue !== "string") {
            setValue(undefined);
            onSelectCallback(selectedValue.item, { setSelectionRange, focus, blur });
        }
    }, [onSelectCallback, blur, focus, setSelectionRange]);
    return (_jsx(MuiAutocomplete, { className: className, componentsProps: {
            paper: { elevation: 8 },
        }, getOptionLabel: getOptionLabel, disableCloseOnSelect: true, disabled: disabled, freeSolo: true, fullWidth: true, PopperComponent: CustomPopper, filterOptions: filterOptions, ListboxComponent: ReactWindowListboxAdapter, onChange: onSelect, onInputChange: onChange, openOnFocus: true, options: autocompleteItems, readOnly: readOnly, renderInput: (params) => (_jsx(TextField, { ...params, variant: variant, inputRef: inputRef, "data-testid": "autocomplete-textfield", placeholder: placeholder, className: cx({ [classes.inputError]: hasError }), size: "small" })), renderOption: (optProps, option, state) => {
            // The return values of renderOption are passed as the _child_ argument to the ListboxComponent.
            // Our ReactWindowListboxAdapter expects a tuple for each item in the list and will itself manage
            // when and which items to render using virtualization.
            //
            // The final as ReactNode cast is to appease the expected return type of renderOption because
            // it does not understand that our ListboxAdapter needs a tuple and not a ReactNode
            return [optProps, option, state];
        }, selectOnFocus: selectOnFocus, size: "small", value: value ?? ReactNull }));
});
