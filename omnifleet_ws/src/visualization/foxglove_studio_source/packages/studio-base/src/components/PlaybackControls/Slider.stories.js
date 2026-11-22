import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useState } from "react";
import { makeStyles } from "tss-react/mui";
import Stack from "@foxglove/studio-base/components/Stack";
import Slider from "./Slider";
const useStyles = makeStyles()((theme) => ({
    customMarker: {
        backgroundColor: theme.palette.background.paper,
        border: "1px solid",
        borderColor: theme.palette.text.primary,
        height: "150%",
        position: "absolute",
        top: "-25%",
        width: 6,
    },
    customRange: {
        backgroundColor: theme.palette.info.dark,
        borderRadius: theme.shape.borderRadius,
        height: "20%",
        left: 0,
        position: "absolute",
    },
    errorTrack: {
        backgroundColor: theme.palette.error.light,
        height: 30,
        width: 300,
    },
    infoTrack: {
        backgroundColor: theme.palette.info.main,
        height: 20,
        width: 500,
    },
}));
export default {
    title: "components/PlaybackControls/Slider",
};
export const Examples = {
    render: function Story() {
        const { classes } = useStyles();
        const [value, setValue] = useState(0.5);
        const [draggableValue, setDraggableValue] = useState(0.25);
        return (_jsxs(Stack, { padding: 4, children: [_jsx("p", { children: "standard (clickable)" }), _jsx("div", { className: classes.errorTrack, children: _jsx(Slider, { onChange: (v) => {
                            setValue(v);
                        }, fraction: value }) }), _jsx("p", { children: "disabled (not clickable)" }), _jsx("div", { className: classes.errorTrack, children: _jsx(Slider, { disabled: true, onChange: (v) => {
                            setValue(v);
                        }, fraction: value }) }), _jsx("p", { children: "no value" }), _jsx("div", { className: classes.errorTrack, children: _jsx(Slider, { onChange: () => {
                            // no-op
                        }, fraction: undefined }) }), _jsx("p", { children: "draggable" }), _jsx("div", { className: classes.infoTrack, children: _jsx(Slider, { onChange: (v) => {
                            setDraggableValue(v);
                        }, fraction: draggableValue }) })] }));
    },
};
export const CustomRenderer = {
    render: function Story() {
        const { classes } = useStyles();
        const [draggableValue, setDraggableValue] = useState(0.25);
        return (_jsxs(Stack, { padding: 4, children: [_jsx("p", { children: "Customize slider UI using renderSlider" }), _jsx("div", { className: classes.infoTrack, children: _jsx(Slider, { onChange: (v) => {
                            setDraggableValue(v);
                        }, fraction: draggableValue, renderSlider: (width) => (_jsxs(_Fragment, { children: [_jsx("div", { className: classes.customRange, style: { width: `${(width ?? 0) * 100}%` } }), _jsx("div", { className: classes.customMarker, style: { left: `${(width ?? 0) * 100}%` } })] })) }) })] }));
    },
};
