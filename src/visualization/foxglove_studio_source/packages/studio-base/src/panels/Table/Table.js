import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
//
// This file incorporates work covered by the following copyright and
// permission notice:
//
//   Copyright 2020-2021 Cruise LLC
//
//   This source code is licensed under the Apache License, Version 2.0,
//   found at http://www.apache.org/licenses/LICENSE-2.0
//   You may not use this file except in compliance with the License.
import PlusIcon from "@mui/icons-material/AddBoxOutlined";
import MinusIcon from "@mui/icons-material/IndeterminateCheckBoxOutlined";
import KeyboardArrowLeftIcon from "@mui/icons-material/KeyboardArrowLeft";
import KeyboardArrowRightIcon from "@mui/icons-material/KeyboardArrowRight";
import KeyboardDoubleArrowLeftIcon from "@mui/icons-material/KeyboardDoubleArrowLeft";
import KeyboardDoubleArrowRightIcon from "@mui/icons-material/KeyboardDoubleArrowRight";
import { Container, IconButton, MenuItem, Select, Typography } from "@mui/material";
import { createColumnHelper, flexRender, getCoreRowModel, getExpandedRowModel, getSortedRowModel, useReactTable, } from "@tanstack/react-table";
import memoizeWeak from "memoize-weak";
import { makeStyles } from "tss-react/mui";
import EmptyState from "@foxglove/studio-base/components/EmptyState";
import Stack from "@foxglove/studio-base/components/Stack";
import TableCell from "./TableCell";
import { sanitizeAccessorPath } from "./sanitizeAccessorPath";
function isTypedArray(value) {
    return (value instanceof Uint8Array ||
        value instanceof Uint8ClampedArray ||
        value instanceof Int8Array ||
        value instanceof Uint16Array ||
        value instanceof Int16Array ||
        value instanceof Uint32Array ||
        value instanceof Int32Array ||
        value instanceof Float32Array ||
        value instanceof Float64Array);
}
const useStyles = makeStyles()((theme, _params, classes) => ({
    table: {
        border: "none",
        width: "100%",
        borderCollapse: "collapse",
        borderSpacing: 0,
    },
    tableRow: {
        svg: { opacity: 0.6 },
        "&:nth-of-type(even)": {
            backgroundColor: theme.palette.action.hover,
        },
        "&:hover": {
            backgroundColor: theme.palette.action.focus,
            [`.${classes.tableData}`]: {
                backgroundColor: theme.palette.action.hover,
                cursor: "pointer",
            },
            svg: { opacity: 0.8 },
        },
        [`.${classes.tableHeader}:first-of-type`]: {
            paddingTop: theme.spacing(0.5),
            paddingBottom: theme.spacing(0.5),
        },
    },
    tableData: {
        border: `1px solid ${theme.palette.divider}`,
        lineHeight: "1.3em",
        padding: `${theme.spacing(0.5)} !important`,
        verticalAlign: "top",
    },
    tableHeader: {
        color: theme.palette.text.primary,
        verticalAlign: "top",
        border: `1px solid ${theme.palette.divider}`,
        lineHeight: "1.3em",
        borderLeftColor: "transparent",
        borderRightColor: "transparent",
        padding: theme.spacing(0.5),
        fontWeight: "bold !important",
        cursor: "pointer",
        width: "auto",
        textAlign: "left",
        "&#expander": { width: 28 },
    },
    sortAsc: {
        borderBottomColor: theme.palette.primary.main,
    },
    sortDesc: {
        borderTopColor: theme.palette.primary.main,
    },
    iconButton: {
        margin: theme.spacing(-0.5),
        "&:hover": {
            backgroundColor: "transparent",
        },
    },
    textContent: {
        maxWidth: "75vw",
        overflow: "hidden",
        textOverflow: "ellipsis",
        whiteSpace: "nowrap",
    },
}));
const columnHelper = createColumnHelper();
const memoizedCellRenderer = memoizeWeak((accessorPath, id) => {
    return function ValueCell(info) {
        const value = info.getValue();
        const row = info.row;
        if (Array.isArray(value) && typeof value[0] !== "object") {
            return JSON.stringify(value);
        }
        if (typeof value === "object" && value != undefined) {
            return (_jsx(TableCell, { row: row, accessorPath: id, children: _jsx(Table, { value: value, accessorPath: accessorPath }) }));
        }
        // Interpolate in case the value is null.
        return _jsx(TextCellContent, { value: `${value}` });
    };
});
function Expander(info) {
    const { classes } = useStyles();
    const { row } = info;
    return (_jsx(IconButton, { className: classes.iconButton, size: "small", "data-testid": `expand-row-${row.index}`, onClick: () => {
            row.toggleExpanded();
        }, children: row.getIsExpanded() ? _jsx(MinusIcon, { fontSize: "small" }) : _jsx(PlusIcon, { fontSize: "small" }) }));
}
function getColumnsFromObject(val, accessorPath) {
    if (isTypedArray(val)) {
        return [
            columnHelper.accessor((row) => row, {
                id: "typedArray",
                header: "",
                cell: (info) => info.getValue(),
            }),
        ];
    }
    const columns = Object.keys(val).map((accessor) => {
        const id = accessorPath.length !== 0 ? `${accessorPath}.${accessor}` : accessor;
        return columnHelper.accessor(accessor, {
            header: accessor,
            id,
            cell: memoizedCellRenderer(accessorPath, id),
        });
    });
    if (accessorPath.length === 0) {
        const expandColumn = columnHelper.display({
            id: "expander",
            header: "",
            cell: Expander,
        });
        columns.unshift(expandColumn);
    }
    return columns;
}
function TextCellContent(props) {
    const { classes } = useStyles();
    return _jsx("div", { className: classes.textContent, children: props.value });
}
export default function Table({ value, accessorPath, }) {
    const isNested = accessorPath.length > 0;
    const { classes, cx } = useStyles();
    const columns = React.useMemo(() => {
        if (
        // eslint-disable-next-line no-restricted-syntax
        value == null ||
            typeof value !== "object" ||
            // eslint-disable-next-line no-restricted-syntax
            (Array.isArray(value) && typeof value[0] !== "object" && value[0] != null)) {
            return [];
        }
        const maybeMessage = Array.isArray(value) ? value[0] ?? {} : value;
        // Strong assumption about structure of data.
        return getColumnsFromObject(maybeMessage, accessorPath);
    }, [accessorPath, value]);
    const [{ pageIndex, pageSize }, setPagination] = React.useState({
        pageIndex: 0,
        pageSize: 10,
    });
    const pagination = React.useMemo(() => ({
        pageIndex,
        pageSize,
    }), [pageIndex, pageSize]);
    const data = React.useMemo(() => {
        return Array.isArray(value) ? value : isTypedArray(value) ? Array.from(value) : [value];
    }, [value]);
    const [expanded, setExpanded] = React.useState({});
    const table = useReactTable({
        autoResetExpanded: false,
        columns,
        data: data.slice(pageIndex * pageSize, (pageIndex + 1) * pageSize),
        getCoreRowModel: getCoreRowModel(),
        getExpandedRowModel: getExpandedRowModel(),
        getSortedRowModel: getSortedRowModel(),
        initialState: { pagination },
        onExpandedChange: setExpanded,
        manualPagination: true,
        pageCount: Math.ceil(data.length / pagination.pageSize),
        onPaginationChange: setPagination,
        state: {
            expanded,
            pagination,
        },
    });
    if (typeof value !== "object" ||
        // eslint-disable-next-line no-restricted-syntax
        value == null ||
        (!isNested && Array.isArray(value) && typeof value[0] !== "object")) {
        return (_jsx(EmptyState, { children: "Cannot render primitive values in a table. Try using the Raw Messages panel instead." }));
    }
    return (_jsxs(_Fragment, { children: [_jsxs("table", { className: classes.table, children: [_jsx("thead", { children: table.getHeaderGroups().map((headerGroup, i) => {
                            return (_jsx("tr", { className: classes.tableRow, children: headerGroup.headers.map((header) => {
                                    const column = header.column;
                                    return (_jsx("th", { className: cx(classes.tableHeader, {
                                            [classes.sortAsc]: column.getIsSorted() === "asc",
                                            [classes.sortDesc]: column.getIsSorted() === "desc",
                                        }), id: column.id, onClick: header.column.getToggleSortingHandler(), "data-testid": `column-header-${sanitizeAccessorPath(column.id)}`, children: flexRender(header.column.columnDef.header, header.getContext()) }, column.id));
                                }) }, i));
                        }) }), _jsx("tbody", { children: table.getRowModel().rows.map((row) => {
                            return (_jsx("tr", { className: classes.tableRow, children: row.getVisibleCells().map((cell) => {
                                    return (_jsx("td", { className: classes.tableData, children: flexRender(cell.column.columnDef.cell, cell.getContext()) }, cell.id));
                                }) }, row.id));
                        }) })] }), !isNested && (_jsx(Container, { maxWidth: "xs", disableGutters: true, children: _jsxs(Stack, { direction: "row", flexWrap: "wrap", gap: 1, paddingX: 0.5, paddingTop: 0.5, alignItems: "center", children: [_jsx(IconButton, { onClick: () => {
                                table.setPageIndex(0);
                            }, disabled: !table.getCanPreviousPage(), children: _jsx(KeyboardDoubleArrowLeftIcon, { fontSize: "small" }) }), _jsx(IconButton, { onClick: () => {
                                table.previousPage();
                            }, disabled: !table.getCanPreviousPage(), children: _jsx(KeyboardArrowLeftIcon, { fontSize: "small" }) }), _jsxs(Typography, { flex: "auto", variant: "inherit", align: "center", noWrap: true, children: ["Page", " ", _jsxs("strong", { children: [table.getState().pagination.pageIndex + 1, " of ", table.getPageOptions().length] })] }), _jsx(IconButton, { onClick: () => {
                                table.nextPage();
                            }, disabled: !table.getCanNextPage(), children: _jsx(KeyboardArrowRightIcon, { fontSize: "small" }) }), _jsx(IconButton, { onClick: () => {
                                table.setPageIndex(table.getPageCount() - 1);
                            }, disabled: !table.getCanNextPage(), children: _jsx(KeyboardDoubleArrowRightIcon, { fontSize: "small" }) }), _jsx(Select, { value: pageSize, size: "small", onChange: (e) => {
                                table.setPageSize(Number(e.target.value));
                            }, MenuProps: { MenuListProps: { dense: true } }, children: [10, 20, 30, 40, 50].map((size) => (_jsx(MenuItem, { value: size, children: `Show ${size}` }, size))) })] }) }))] }));
}
