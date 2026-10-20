// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
//
// This file incorporates work covered by the following copyright and
// permission notice:
//
//   Copyright 2018-2021 Cruise LLC
//
//   This source code is licensed under the Apache License, Version 2.0,
//   found at http://www.apache.org/licenses/LICENSE-2.0
//   You may not use this file except in compliance with the License.
import * as _ from "lodash-es";
import Rpc from "@foxglove/studio-base/util/Rpc";
import { setupMainThreadRpc } from "@foxglove/studio-base/util/RpcMainThreadUtils";
export default class WebWorkerManager {
    #createWorker;
    #maxWorkerCount;
    #workerStates;
    #allListeners;
    constructor(createWorker, maxWorkerCount) {
        this.#createWorker = createWorker;
        this.#maxWorkerCount = maxWorkerCount;
        this.#workerStates = new Array(maxWorkerCount);
        this.#allListeners = new Set();
    }
    testing_workerCount() {
        return this.#workerStates.filter(Boolean).length;
    }
    testing_getWorkerState(id) {
        return this.#workerStates.find((workerState) => workerState?.listenerIds.includes(id));
    }
    registerWorkerListener(id) {
        if (this.#allListeners.has(id)) {
            throw new Error("cannot register the same listener id twice");
        }
        this.#allListeners.add(id);
        const currentWorkerCount = this.#workerStates.filter(Boolean).length;
        if (currentWorkerCount < this.#maxWorkerCount) {
            const worker = this.#createWorker();
            const rpc = new Rpc(worker);
            setupMainThreadRpc(rpc);
            const emptyIndex = _.findIndex(this.#workerStates, (x) => !x);
            this.#workerStates[emptyIndex] = { worker, rpc, listenerIds: [id] };
            return rpc;
        }
        const workerStateByListenerCount = _.sortBy(this.#workerStates.filter(Boolean), (workerState) => workerState?.listenerIds.length);
        const workerState = workerStateByListenerCount[0];
        if (!workerState) {
            throw new Error("no worker state");
        }
        workerState.listenerIds.push(id);
        return workerState.rpc;
    }
    unregisterWorkerListener(id) {
        if (!this.#allListeners.has(id)) {
            throw new Error("Cannot find listener to unregister");
        }
        this.#allListeners.delete(id);
        const workerStateIndex = _.findIndex(this.#workerStates, (workerState) => {
            if (!workerState) {
                return false;
            }
            return workerState.listenerIds.includes(id);
        });
        const workerState = this.#workerStates[workerStateIndex];
        if (workerStateIndex >= 0 && workerState) {
            workerState.listenerIds = workerState.listenerIds.filter((_id) => _id !== id);
            if (workerState.listenerIds.length === 0) {
                this.#workerStates[workerStateIndex] = undefined;
                workerState.worker.terminate();
                workerState.rpc.terminate();
            }
        }
    }
}
