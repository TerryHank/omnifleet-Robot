import { jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { useMemo } from "react";
import { makeStyles } from "tss-react/mui";
const useStyles = makeStyles()(() => ({
    root: {
        top: 0,
        bottom: 0,
        position: "absolute",
        pointerEvents: "none",
        willChange: "transform",
        visibility: "hidden",
    },
}));
export function VerticalBarWrapper({ children, scales, xValue, }) {
    const { classes } = useStyles();
    const positionX = useMemo(() => {
        const xScale = scales?.x;
        if (!xScale || xValue == undefined) {
            return;
        }
        const pixels = xScale.pixelMax - xScale.pixelMin;
        const range = xScale.max - xScale.min;
        if (pixels === 0 || range === 0) {
            return;
        }
        const pos = (xValue - xScale.min) / (range / pixels) + xScale.pixelMin;
        // don't show hoverbar if it falls outsize our boundary
        if (pos < xScale.pixelMin || pos > xScale.pixelMax) {
            return;
        }
        return pos;
    }, [scales?.x, xValue]);
    const style = useMemo(() => {
        if (positionX == undefined || isNaN(positionX)) {
            return { visibility: "hidden", transform: undefined };
        }
        return { visibility: "visible", transform: `translateX(${positionX}px)` };
    }, [positionX]);
    return (_jsx("div", { className: classes.root, style: style, children: children }));
}
