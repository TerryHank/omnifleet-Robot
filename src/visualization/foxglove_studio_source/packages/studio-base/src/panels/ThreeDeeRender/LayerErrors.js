// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import EventEmitter from "eventemitter3";
import Logger from "@foxglove/log";
const TOPIC_PATH = ["topics", ""];
export class NodeError {
    path;
    errorsById;
    children;
    constructor(path) {
        this.path = path;
    }
    errorMessage() {
        if (this.errorsById && this.errorsById.size > 0) {
            const errorMessages = Array.from(this.errorsById.values());
            return errorMessages.join(`\n`);
        }
        else {
            return undefined;
        }
    }
    errorAtPath(path) {
        // eslint-disable-next-line @typescript-eslint/no-this-alias
        let node = this;
        for (const segment of path) {
            node = node.children?.get(segment);
            if (!node) {
                return undefined;
            }
        }
        return node.errorMessage();
    }
    clone() {
        const clone = new NodeError(this.path);
        clone.errorsById = this.errorsById;
        clone.children = this.children;
        return clone;
    }
}
const log = Logger.getLogger(__filename);
export class LayerErrors extends EventEmitter {
    errors = new NodeError([]);
    add(path, errorId, errorMessage) {
        // Get or create the node for the given path
        let node = this.errors;
        for (const segment of path) {
            if (!node.children) {
                node.children = new Map();
            }
            if (!node.children.has(segment)) {
                node.children.set(segment, new NodeError([...node.path, segment]));
            }
            node = node.children.get(segment);
        }
        // Create the error map if it does not already exist
        node.errorsById ??= new Map();
        // Onlu log the first error message per path+id for performance
        const prevErrorMessage = node.errorsById.get(errorId);
        if (prevErrorMessage == undefined) {
            log.warn(`[${path.join(" > ")}] ${errorMessage}`);
        }
        // Add or update the error
        if (errorMessage !== prevErrorMessage) {
            node.errorsById.set(errorId, errorMessage);
            this.emit("update", path, errorId, errorMessage);
        }
    }
    addToTopic(topicId, errorId, errorMessage) {
        TOPIC_PATH[1] = topicId;
        this.add(TOPIC_PATH, errorId, errorMessage);
    }
    hasError(path, errorId) {
        const node = this.#getNode(path);
        return node?.errorsById?.has(errorId) === true;
    }
    remove(path, errorId) {
        const node = this.#getNode(path);
        if (node?.errorsById?.has(errorId) === true) {
            node.errorsById.delete(errorId);
            this.emit("remove", path, errorId);
        }
    }
    removeFromTopic(topicId, errorId) {
        TOPIC_PATH[1] = topicId;
        this.remove(TOPIC_PATH, errorId);
    }
    /**
     * If value is falsy then add error to path, otherwise remove error from settings path
     * @param value - value to check, if false, add error, if true, remove error
     * @param path  - path to add/remove error
     * @param errorId - id unique to error
     * @param errorMessage - error message
     */
    // eslint-disable-next-line @foxglove/no-boolean-parameters
    errorIfFalse(value, path, errorId, errorMessage) {
        if (!value) {
            this.add(path, errorId, errorMessage);
        }
        else {
            this.remove(path, errorId);
        }
    }
    clearPath(path) {
        const node = this.#getNode(path);
        if (!node) {
            return;
        }
        let cleared = false;
        if (node.children && node.children.size > 0) {
            node.children.clear();
            cleared = true;
        }
        if (node.errorsById && node.errorsById.size > 0) {
            node.errorsById.clear();
            cleared = true;
        }
        if (cleared) {
            this.emit("clear", path);
        }
    }
    clearTopic(topicId) {
        TOPIC_PATH[1] = topicId;
        this.clearPath(TOPIC_PATH);
    }
    clear() {
        this.clearPath([]);
    }
    #getNode(path) {
        let node = this.errors;
        for (const segment of path) {
            node = node.children?.get(segment);
            if (!node) {
                return undefined;
            }
        }
        return node;
    }
}
