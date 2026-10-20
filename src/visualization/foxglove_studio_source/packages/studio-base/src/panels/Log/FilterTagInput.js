import { jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { Dismiss12Filled } from "@fluentui/react-icons";
import { TextField, inputBaseClasses } from "@mui/material";
import Autocomplete, { autocompleteClasses } from "@mui/material/Autocomplete";
import { makeStyles } from "tss-react/mui";
const useStyles = makeStyles()((theme) => ({
    input: {
        [`.${inputBaseClasses.root}.${inputBaseClasses.sizeSmall}.${inputBaseClasses.adornedStart}`]: {
            padding: theme.spacing(0.375, 0.5),
            gap: theme.spacing(0.375),
            [`.${inputBaseClasses.inputSizeSmall}`]: {
                padding: theme.spacing(0.425, 0.5),
            },
        },
    },
    chip: {
        [`&.${autocompleteClasses.tag}`]: {
            margin: 0,
        },
    },
}));
export function FilterTagInput({ items, suggestions, onChange, }) {
    const { classes } = useStyles();
    return (_jsx(Autocomplete, { value: items, multiple: true, onChange: (_event, value) => {
            onChange(value);
        }, id: "tags-filled", options: suggestions, freeSolo: true, fullWidth: true, ChipProps: {
            className: classes.chip,
            variant: "filled",
            size: "small",
            deleteIcon: _jsx(Dismiss12Filled, {}),
        }, renderInput: (params) => (_jsx(TextField, { ...params, size: "small", className: classes.input, placeholder: "\u641C\u7D22\u7B5B\u9009\u6761\u4EF6" })) }));
}
