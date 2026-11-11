import { jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { forwardRef } from "react";
import { makeStyles } from "tss-react/mui";
const useStyles = makeStyles({ name: "FoxgloveStack" })((theme, props) => ({
    root: {
        display: props.inline === true ? "inline-flex" : "flex",
        flexDirection: props.direction,
        flex: props.flex,
        flexBasis: props.flexBasis,
        flexShrink: props.flexShrink,
        flexGrow: props.flexGrow,
        flexWrap: props.flexWrap,
        justifyContent: props.justifyContent,
        alignItems: props.alignItems,
        alignContent: props.alignContent,
        alignSelf: props.alignSelf,
        order: props.order,
        overflow: props.overflow,
        overflowX: props.overflowX,
        overflowY: props.overflowY,
        position: props.position,
        ...(props.zeroMinWidth === true && {
            minWidth: 0,
        }),
        ...(props.fullHeight === true && {
            height: "100%",
        }),
        ...(props.fullWidth === true && {
            width: "100%",
        }),
        ...(props.gap != undefined && {
            gap: theme.spacing(props.gap),
        }),
        ...(props.gapX != undefined && {
            rowGap: theme.spacing(props.gapX),
        }),
        ...(props.gapY != undefined && {
            columnGap: theme.spacing(props.gapY),
        }),
        ...(props.padding != undefined && {
            padding: theme.spacing(props.padding),
        }),
        ...(props.paddingX != undefined && {
            paddingLeft: theme.spacing(props.paddingX),
            paddingRight: theme.spacing(props.paddingX),
        }),
        ...(props.paddingY != undefined && {
            paddingTop: theme.spacing(props.paddingY),
            paddingBottom: theme.spacing(props.paddingY),
        }),
        ...(props.paddingTop != undefined && {
            paddingTop: theme.spacing(props.paddingTop),
        }),
        ...(props.paddingBottom != undefined && {
            paddingBottom: theme.spacing(props.paddingBottom),
        }),
        ...(props.paddingLeft != undefined && {
            paddingLeft: theme.spacing(props.paddingLeft),
        }),
        ...(props.paddingRight != undefined && {
            paddingRight: theme.spacing(props.paddingRight),
        }),
        ...(props.paddingBlock != undefined && {
            paddingBlock: theme.spacing(props.paddingBlock),
        }),
        ...(props.paddingBlockStart != undefined && {
            paddingBlockStart: theme.spacing(props.paddingBlockStart),
        }),
        ...(props.paddingBlockEnd != undefined && {
            paddingBlockEnd: theme.spacing(props.paddingBlockEnd),
        }),
        ...(props.paddingInline != undefined && {
            paddingInline: theme.spacing(props.paddingInline),
        }),
        ...(props.paddingInlineStart != undefined && {
            paddingInlineStart: theme.spacing(props.paddingInlineStart),
        }),
        ...(props.paddingInlineEnd != undefined && {
            paddingInlineEnd: theme.spacing(props.paddingInlineEnd),
        }),
    },
}));
export default forwardRef(function Stack(props, ref) {
    const { alignItems, alignSelf, children, className, direction = "column", flex, flexBasis, flexGrow, flexShrink, flexWrap, fullHeight = false, fullWidth = false, gap, gapX, gapY, inline = false, justifyContent, order, overflow, overflowX, overflowY, padding, paddingBottom, paddingLeft, paddingRight, paddingTop, paddingX, paddingY, paddingBlock, paddingBlockStart, paddingBlockEnd, paddingInline, paddingInlineStart, paddingInlineEnd, position, style, zeroMinWidth = false, ...rest } = props;
    const { classes, cx } = useStyles({
        alignItems,
        alignSelf,
        direction,
        flex,
        flexBasis,
        flexGrow,
        flexShrink,
        flexWrap,
        fullHeight,
        fullWidth,
        gap,
        gapX,
        gapY,
        inline,
        justifyContent,
        order,
        overflow,
        overflowX,
        overflowY,
        padding,
        paddingBottom,
        paddingLeft,
        paddingRight,
        paddingTop,
        paddingX,
        paddingY,
        paddingBlock,
        paddingBlockStart,
        paddingBlockEnd,
        paddingInline,
        paddingInlineStart,
        paddingInlineEnd,
        position,
        zeroMinWidth,
    });
    return (_jsx("div", { ref: ref, className: cx(classes.root, className), style: style, ...rest, children: children }));
});
