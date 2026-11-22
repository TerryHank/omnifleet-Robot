import { jsx as _jsx } from "react/jsx-runtime";
import { makeStyles } from "tss-react/mui";
const useStyles = makeStyles()((theme) => ({
    root: {
        padding: theme.spacing(0, 0.5),
        textDecoration: "inherit",
        whiteSpace: "pre-line",
    },
}));
export function DiffSpan(props) {
    const { children, style } = props;
    const { classes } = useStyles();
    return (_jsx("span", { className: classes.root, style: style, children: children }));
}
