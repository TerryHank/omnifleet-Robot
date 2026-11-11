import { jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { useTheme } from "@mui/material";
import { useEffect } from "react";
import { fromDate } from "@foxglove/rostime";
import MockMessagePipelineProvider from "@foxglove/studio-base/components/MessagePipeline/MockMessagePipelineProvider";
import { ProblemsList } from "@foxglove/studio-base/components/ProblemsList";
import { useProblemsActions } from "@foxglove/studio-base/context/ProblemsContext";
import { PlayerPresence } from "@foxglove/studio-base/players/types";
import ProblemsContextProvider from "@foxglove/studio-base/providers/ProblemsContextProvider";
import WorkspaceContextProvider from "@foxglove/studio-base/providers/WorkspaceContextProvider";
function makeProblems() {
    return [
        {
            severity: "error",
            message: "Connection lost",
            tip: "A tip that we might want to show the user",
            error: Object.assign(new Error("Fake Error"), {
                stack: `Error: Original Error
at Story (https://603ec8bf7908b500231841e2-nozcuvybhv.capture.chromatic.com/studio-base-src-components-ProblemsList-stories.039002bb.iframe.bundle.js:58:28)
at undecoratedStoryFn (https://603ec8bf7908b500231841e2-nozcuvybhv.capture.chromatic.com/sb-preview/runtime.mjs:34:2794)
at hookified (https://603ec8bf7908b500231841e2-nozcuvybhv.capture.chromatic.com/sb-preview/runtime.mjs:7:17032)
at https://603ec8bf7908b500231841e2-nozcuvybhv.capture.chromatic.com/sb-preview/runtime.mjs:34:1915
at jsxDecorator (https://603ec8bf7908b500231841e2-nozcuvybhv.capture.chromatic.com/1983.4cb8db42.iframe.bundle.js:13838:1100)
at hookified (https://603ec8bf7908b500231841e2-nozcuvybhv.capture.chromatic.com/sb-preview/runtime.mjs:7:17032)
at https://603ec8bf7908b500231841e2-nozcuvybhv.capture.chromatic.com/sb-preview/runtime.mjs:34:1454
at https://603ec8bf7908b500231841e2-nozcuvybhv.capture.chromatic.com/sb-preview/runtime.mjs:34:1915
at Ch (https://603ec8bf7908b500231841e2-nozcuvybhv.capture.chromatic.com/1983.4cb8db42.iframe.bundle.js:47712:137)
at ck (https://603ec8bf7908b500231841e2-nozcuvybhv.capture.chromatic.com/1983.4cb8db42.iframe.bundle.js:47822:460)`,
            }),
        },
        {
            severity: "warn",
            message: "Connection lost",
        },
        {
            severity: "info",
            message: "Connection lost",
            tip: "A tip that we might want to show the user",
        },
    ];
}
export default {
    title: "components/ProblemsList",
    component: ProblemsList,
    decorators: [
        (Story) => {
            const theme = useTheme();
            return (_jsx(WorkspaceContextProvider, { children: _jsx("div", { style: { height: "100%", background: theme.palette.background.paper }, children: _jsx(ProblemsContextProvider, { children: _jsx(Story, {}) }) }) }));
        },
    ],
};
const START_TIME = fromDate(new Date(2022, 1, 22, 1, 11, 11));
const END_TIME = fromDate(new Date(2022, 1, 22, 22, 22, 22));
const TOPICS = [];
export const Default = {
    render: function Story() {
        return (_jsx(MockMessagePipelineProvider, { startTime: START_TIME, endTime: END_TIME, presence: PlayerPresence.INITIALIZING, children: _jsx(ProblemsList, {}) }));
    },
};
export const DefaultChinese = {
    ...Default,
    parameters: { forceLanguage: "zh" },
};
export const DefaultJapanese = {
    ...Default,
    parameters: { forceLanguage: "ja" },
};
export const WithErrors = {
    render: function Story() {
        return (_jsx(MockMessagePipelineProvider, { startTime: START_TIME, endTime: END_TIME, topics: TOPICS, presence: PlayerPresence.RECONNECTING, problems: makeProblems(), children: _jsx(ProblemsList, {}) }));
    },
};
export const WithErrorsChinese = {
    ...WithErrors,
    parameters: { forceLanguage: "zh" },
};
export const WithErrorsJapanese = {
    ...WithErrors,
    parameters: { forceLanguage: "ja" },
};
export const WithSessionProblems = {
    render: function Story() {
        const problemsActions = useProblemsActions();
        useEffect(() => {
            problemsActions.setProblem("tag-1", {
                message: "Session problem error",
                severity: "error",
                tip: "Something really bad happened",
            });
            problemsActions.setProblem("tag-2", {
                message: "Session problem warn",
                severity: "warn",
                tip: "Something kinda bad happened",
            });
        }, [problemsActions]);
        return (_jsx(MockMessagePipelineProvider, { startTime: START_TIME, endTime: END_TIME, topics: TOPICS, presence: PlayerPresence.RECONNECTING, problems: makeProblems(), children: _jsx(WorkspaceContextProvider, { children: _jsx(ProblemsList, {}) }) }));
    },
};
