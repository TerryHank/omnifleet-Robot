import { PlayerProblem } from "@foxglove/studio-base/players/types";
/**
 * Manages a set of PlayerProblems keyed by ID. Calls to problems() will return the same object as
 * long as problems have not been added/removed; this helps the player pipeline to know when it
 * needs to re-process player problems.
 */
export default class PlayerProblemManager {
    #private;
    /**
     * Returns the current set of problems. Subsequent calls will return the same object as long as
     * problems have not been added/removed.
     */
    problems(): PlayerProblem[];
    addProblem(id: string, problem: PlayerProblem): void;
    hasProblem(id: string): boolean;
    removeProblem(id: string): boolean;
    removeProblems(predicate: (id: string, problem: PlayerProblem) => boolean): boolean;
    clear(): void;
}
