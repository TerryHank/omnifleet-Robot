import { jsx as _jsx, Fragment as _Fragment, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { ErrorCircle16Regular, Info16Regular, Warning16Regular } from "@fluentui/react-icons";
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import { Accordion, AccordionDetails, AccordionSummary, Divider, Typography, accordionSummaryClasses, useTheme, } from "@mui/material";
import { useMemo } from "react";
import { useTranslation } from "react-i18next";
import { makeStyles } from "tss-react/mui";
import EmptyState from "@foxglove/studio-base/components/EmptyState";
import { useMessagePipeline, } from "@foxglove/studio-base/components/MessagePipeline";
import Stack from "@foxglove/studio-base/components/Stack";
import { useProblemsStore, } from "@foxglove/studio-base/context/ProblemsContext";
const useStyles = makeStyles()((theme) => ({
    acccordion: {
        background: "none",
        boxShadow: "none",
        borderBottom: `1px solid ${theme.palette.divider}`,
        "&:before": {
            display: "none",
        },
        "&.Mui-expanded": {
            margin: 0,
        },
    },
    accordionDetails: {
        display: "flex",
        flexDirection: "column",
        fontFamily: theme.typography.fontMonospace,
        fontSize: "0.6875rem",
        padding: theme.spacing(1.125),
        gap: theme.spacing(1),
    },
    acccordionSummary: {
        height: 30,
        minHeight: "auto",
        padding: theme.spacing(0, 0.5, 0, 0.75),
        fontWeight: 500,
        "&:hover": {
            backgroundColor: theme.palette.action.hover,
        },
        "&.Mui-expanded": {
            minHeight: "auto",
        },
        [`& .${accordionSummaryClasses.content}`]: {
            gap: theme.spacing(0.5),
            overflow: "hidden",
            alignItems: "center",
            margin: "0 !important",
        },
        [`& .${accordionSummaryClasses.expandIconWrapper}`]: {
            transform: "rotate(-90deg)",
        },
        [`& .${accordionSummaryClasses.expandIconWrapper}.Mui-expanded`]: {
            transform: "rotate(0deg)",
        },
    },
    detailsText: {
        color: theme.palette.text.primary,
        fontSize: theme.typography.caption.fontSize,
        lineHeight: 1.5,
        whiteSpace: "pre-wrap",
        maxHeight: "30vh",
        overflow: "auto",
        flex: 1,
        backgroundColor: theme.palette.action.hover,
        padding: theme.spacing(1),
    },
    icon: {
        flex: "none",
    },
}));
const EMPTY_PLAYER_PROBLEMS = [];
const selectPlayerProblems = ({ playerState }) => playerState.problems ?? EMPTY_PLAYER_PROBLEMS;
const selectProblems = (store) => store.problems;
function ProblemIcon({ severity }) {
    const { palette } = useTheme();
    const { classes } = useStyles();
    switch (severity) {
        case "warn":
            return _jsx(Warning16Regular, { className: classes.icon, primaryFill: palette.warning.main });
        case "error":
            return _jsx(ErrorCircle16Regular, { className: classes.icon, primaryFill: palette.error.main });
        case "info":
            return _jsx(Info16Regular, { className: classes.icon, primaryFill: palette.info.main });
        default:
            return _jsx(_Fragment, {});
    }
}
function ProblemDetails(props) {
    const { t } = useTranslation("problemsList");
    const { details, tip } = props;
    const { classes } = useStyles();
    const content = useMemo(() => {
        if (details instanceof Error) {
            return _jsx("div", { className: classes.detailsText, children: details.message });
        }
        else if (details != undefined && details !== "") {
            return (_jsx(Typography, { style: { whiteSpace: "pre-line" /* allow newlines in the details message */ }, children: details }));
        }
        else if (tip != undefined && tip !== "") {
            return undefined;
        }
        return t("noDetailsProvided");
    }, [classes, details, tip, t]);
    return (_jsxs(AccordionDetails, { className: classes.accordionDetails, children: [tip && _jsx("div", { children: tip }), content] }));
}
export function ProblemsList() {
    const { t } = useTranslation("problemsList");
    const { classes } = useStyles();
    const playerProblems = useMessagePipeline(selectPlayerProblems);
    const sessionProblems = useProblemsStore(selectProblems);
    const allProblems = useMemo(() => {
        return [...sessionProblems, ...playerProblems];
    }, [sessionProblems, playerProblems]);
    if (allProblems.length === 0) {
        return _jsx(EmptyState, { children: t("noProblemsFound") });
    }
    return (_jsx(Stack, { fullHeight: true, flex: "auto", overflow: "auto", children: allProblems.map((problem, idx) => (_jsxs(Accordion, { className: classes.acccordion, TransitionProps: { unmountOnExit: true }, defaultExpanded: true, children: [_jsxs(AccordionSummary, { className: classes.acccordionSummary, expandIcon: _jsx(ArrowDropDownIcon, {}), title: problem.message, children: [_jsx(ProblemIcon, { severity: problem.severity }), _jsx(Typography, { variant: "inherit", noWrap: true, children: problem.message })] }), _jsx(Divider, {}), _jsx(ProblemDetails, { details: problem.error, tip: problem.tip })] }, `${idx}.${problem.severity}.${problem.message}`))) }));
}
