// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import * as Comlink from "comlink";
import { abortSignalTransferHandler } from "@foxglove/comlink-transfer-handlers";
import { IteratorCursor } from "./IteratorCursor";
export class WorkerIterableSourceWorker {
    _source;
    constructor(source) {
        this._source = source;
    }
    async initialize() {
        return await this._source.initialize();
    }
    messageIterator(args) {
        return Comlink.proxy(this._source.messageIterator(args));
    }
    async getBackfillMessages(args, 
    // abortSignal is a separate argument so it can be proxied by comlink since AbortSignal is not
    // clonable (and needs to signal across the worker boundary)
    abortSignal) {
        return await this._source.getBackfillMessages({
            ...args,
            abortSignal,
        });
    }
    getMessageCursor(args, abort) {
        const iter = this._source.messageIterator(args);
        const cursor = new IteratorCursor(iter, abort);
        return Comlink.proxy(cursor);
    }
}
Comlink.transferHandlers.set("abortsignal", abortSignalTransferHandler);
