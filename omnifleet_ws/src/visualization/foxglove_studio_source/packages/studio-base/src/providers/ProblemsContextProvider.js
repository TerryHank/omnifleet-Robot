import { jsx as _jsx } from "react/jsx-runtime";
import { useState } from "react";
import { create } from "zustand";
import { ProblemsContext, } from "@foxglove/studio-base/context/ProblemsContext";
function createProblemsStore() {
    return create((set, get) => {
        return {
            problems: [],
            actions: {
                clearProblem: (tag) => {
                    set({
                        problems: get().problems.filter((prob) => prob.tag !== tag),
                    });
                },
                setProblem: (tag, problem) => {
                    const newProblems = get().problems.filter((prob) => prob.tag !== tag);
                    set({
                        problems: [{ tag, ...problem }, ...newProblems],
                    });
                },
            },
        };
    });
}
export default function ProblemsContextProvider({ children, }) {
    const [store] = useState(createProblemsStore);
    return _jsx(ProblemsContext.Provider, { value: store, children: children });
}
