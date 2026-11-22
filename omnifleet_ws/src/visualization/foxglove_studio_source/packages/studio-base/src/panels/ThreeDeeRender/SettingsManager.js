// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import EventEmitter from "eventemitter3";
import { produce } from "immer";
import { LayerErrors } from "./LayerErrors";
export class SettingsManager extends EventEmitter {
    errors = new LayerErrors();
    #nodesByKey = new Map();
    #root = { children: {} };
    #globalSettingsEntryValidators = [];
    constructor(baseTree) {
        super();
        this.#root = { children: baseTree };
        this.errors.on("update", this.handleErrorUpdate);
        this.errors.on("remove", this.handleErrorUpdate);
        this.errors.on("clear", this.handleErrorUpdate);
    }
    setNodesForKey(key, nodes) {
        nodes.forEach((entry) => {
            this.#globalSettingsEntryValidators.forEach((validator) => {
                validator(entry, this.errors);
            });
        });
        this.#root = produce(this.#root, (draft) => {
            // Delete all previous nodes for this key
            const prevNodes = this.#nodesByKey.get(key);
            if (prevNodes) {
                for (const { path } of prevNodes) {
                    removeNodeAtPath(draft, path);
                }
            }
            // Add the new nodes
            for (const { path, node } of nodes) {
                node.error ??= this.errors.errors.errorAtPath(path);
                node.label ??= path[path.length - 1];
                node.defaultExpansionState ??= "collapsed";
                addNodeAtPath(draft, path, node);
            }
        });
        // Update the map of nodes by key
        this.#nodesByKey.set(key, nodes);
        this.emit("update");
    }
    setLabel(path, label) {
        this.#root = produce(this.#root, (draft) => {
            setLabelAtPath(draft, path, label);
        });
        this.emit("update");
    }
    clearChildren(path) {
        this.#root = produce(this.#root, (draft) => {
            clearChildren(draft, path);
        });
        this.emit("update");
    }
    tree() {
        return this.#root.children;
    }
    handleAction = (action) => {
        const path = action.payload.path;
        // Walk the settings tree down to the end of the path, firing any action
        // handlers along the way
        let curNode = this.#root;
        curNode.handler?.(action);
        for (const segment of path) {
            const nextNode = curNode.children?.[segment];
            if (!nextNode) {
                return;
            }
            nextNode.handler?.(action);
            curNode = nextNode;
        }
    };
    /** Add Validator function that can run over nodes `set` on the tree and update error state accordingly */
    addNodeValidator = (nodeValidator) => {
        this.#globalSettingsEntryValidators.push(nodeValidator);
    };
    removeNodeValidator = (nodeValidator) => {
        this.#globalSettingsEntryValidators = this.#globalSettingsEntryValidators.filter((v) => v !== nodeValidator);
    };
    handleErrorUpdate = (path) => {
        this.#root = produce(this.#root, (draft) => {
            if (path.length === 0) {
                return { ...draft };
            }
            let curNode = draft;
            for (const segment of path) {
                const nextNode = curNode.children?.[segment];
                if (!nextNode) {
                    curNode.children = { ...curNode.children };
                    return draft;
                }
                curNode = nextNode;
            }
            curNode.error = this.errors.errors.errorAtPath(path);
            return draft;
        });
        this.emit("update");
    };
}
function removeNodeAtPath(root, path) {
    if (path.length === 0) {
        return false;
    }
    const segment = path[0];
    const nextNode = root.children?.[segment];
    if (!nextNode) {
        return false;
    }
    if (path.length === 1) {
        const hasEntry = root.children?.[segment] != undefined;
        if (hasEntry) {
            root.children[segment] = undefined;
        }
        return hasEntry;
    }
    return removeNodeAtPath(nextNode, path.slice(1));
}
function clearChildren(root, path) {
    if (path.length === 0) {
        return;
    }
    const segment = path[0];
    const nextNode = root.children?.[segment];
    if (!nextNode) {
        return;
    }
    if (path.length === 1) {
        nextNode.children = undefined;
        return;
    }
    clearChildren(nextNode, path.slice(1));
}
function addNodeAtPath(root, path, node) {
    if (path.length === 0) {
        throw new Error(`Empty path for settings node "${node.label}"`);
    }
    // Recursively walk/build the settings tree down to the end of the path except
    // for the last segment, which is the node to add
    let curNode = root;
    for (let i = 0; i < path.length - 1; i++) {
        const segment = path[i];
        if (!curNode.children) {
            curNode.children = {};
        }
        if (!curNode.children[segment]) {
            curNode.children[segment] = {};
        }
        curNode = curNode.children[segment];
    }
    // Assign the node to the last segment of the path
    const lastSegment = path[path.length - 1];
    if (!curNode.children) {
        curNode.children = {};
    }
    curNode.children[lastSegment] = node;
}
function setLabelAtPath(root, path, label) {
    if (path.length === 0) {
        throw new Error(`Empty path for settings label "${label}"`);
    }
    // Recursively walk/build the settings tree down to the end of the path
    let curNode = root;
    for (const segment of path) {
        if (!curNode.children) {
            curNode.children = {};
        }
        if (!curNode.children[segment]) {
            curNode.children[segment] = {};
        }
        curNode = curNode.children[segment];
    }
    curNode.label = label;
}
