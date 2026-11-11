import { jsx as _jsx } from "react/jsx-runtime";
import tinycolor from "tinycolor2";
import { makeStyles } from "tss-react/mui";
function calculateBorderColor(theme, color) {
    const parsedColor = tinycolor(color);
    return parsedColor.isValid()
        ? theme.palette.getContrastText(parsedColor.toHexString())
        : theme.palette.text.primary;
}
const useStyles = makeStyles()((theme) => ({
    root: {
        // Color on top of white/black diagonal gradient. Color must be specified as a gradient because a
        // background color can't be stacked on top of a background image.
        backgroundImage: `linear-gradient(to bottom right, white 50%, black 50%)`,
        borderRadius: theme.shape.borderRadius,
        display: "inline-flex",
        aspectRatio: "1/1",
        flexShrink: 0,
    },
    swatch: {
        aspectRatio: "1/1",
    },
    sizeSmall: {
        height: theme.spacing(2),
        width: theme.spacing(2),
    },
    sizeMedium: {
        height: theme.spacing(2),
        width: theme.spacing(2),
    },
    sizeLarge: {
        height: theme.spacing(3),
        width: theme.spacing(3),
    },
}));
export function ColorSwatch(props) {
    const { color, size = "medium", className, ...rest } = props;
    const { classes, cx, theme } = useStyles();
    return (_jsx("div", { className: cx(classes.root, {
            [classes.sizeSmall]: size === "small",
            [classes.sizeMedium]: size === "medium",
            [classes.sizeLarge]: size === "large",
        }, className), ...rest, children: _jsx("div", { title: color, className: classes.swatch, style: {
                backgroundColor: color,
                border: `1px solid ${calculateBorderColor(theme, color)}`,
            } }) }));
}
