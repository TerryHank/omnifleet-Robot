/// <reference types="react" />
import { StoreApi } from "zustand";
import { Immutable } from "@foxglove/studio";
import { PlayerProblem } from "@foxglove/studio-base/players/types";
export type SessionProblem = PlayerProblem;
type TaggedProblem = SessionProblem & {
    tag: string;
};
export type ProblemsContextStore = Immutable<{
    problems: TaggedProblem[];
    actions: {
        clearProblem: (tag: string) => void;
        setProblem: (tag: string, problem: Immutable<SessionProblem>) => void;
    };
}>;
export declare const ProblemsContext: import("react").Context<StoreApi<{
    readonly problems: readonly {
        readonly severity: import("../util/sendNotification").NotificationSeverity;
        readonly message: string;
        readonly error?: {
            readonly name: string;
            readonly message: string;
            readonly stack?: string | undefined;
            readonly cause?: unknown;
        } | undefined;
        readonly tip?: string | undefined;
        readonly tag: string;
    }[];
    readonly actions: {
        readonly clearProblem: (tag: string) => void;
        readonly setProblem: (tag: string, problem: Immutable<SessionProblem>) => void;
    };
}> | undefined>;
/**
 * Fetches values from the problems store.
 */
export declare function useProblemsStore<T>(selector: (store: ProblemsContextStore) => T): T;
/**
 * Convenience hook for accessing problems store actions.
 */
export declare function useProblemsActions(): ProblemsContextStore["actions"];
export {};
