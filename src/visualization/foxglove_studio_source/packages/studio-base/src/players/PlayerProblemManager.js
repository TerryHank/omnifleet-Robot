// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
/**
 * Manages a set of PlayerProblems keyed by ID. Calls to problems() will return the same object as
 * long as problems have not been added/removed; this helps the player pipeline to know when it
 * needs to re-process player problems.
 */
export default class PlayerProblemManager {
    #problemsById = new Map();
    #problems;
    /**
     * Returns the current set of problems. Subsequent calls will return the same object as long as
     * problems have not been added/removed.
     */
    problems() {
        return (this.#problems ??= Array.from(this.#problemsById.values()));
    }
    addProblem(id, problem) {
        console[problem.severity].call(console, "Player problem", id, problem);
        this.#problemsById.set(id, problem);
        this.#problems = undefined;
    }
    hasProblem(id) {
        return this.#problemsById.has(id);
    }
    removeProblem(id) {
        const changed = this.#problemsById.delete(id);
        if (changed) {
            this.#problems = undefined;
        }
        return changed;
    }
    removeProblems(predicate) {
        let changed = false;
        for (const [id, problem] of this.#problemsById) {
            if (predicate(id, problem)) {
                if (this.#problemsById.delete(id)) {
                    changed = true;
                }
            }
        }
        if (changed) {
            this.#problems = undefined;
        }
        return changed;
    }
    clear() {
        this.#problemsById.clear();
        this.#problems = undefined;
    }
}
