// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import * as Comlink from "comlink";
import { abortSignalTransferHandler } from "@foxglove/comlink-transfer-handlers";
import { ComlinkWrap } from "@foxglove/den/worker";
Comlink.transferHandlers.set("abortsignal", abortSignalTransferHandler);
export class WorkerIterableSource {
    #args;
    #sourceWorkerRemote;
    #disposeRemote;
    constructor(args) {
        this.#args = args;
    }
    async initialize() {
        this.#disposeRemote?.();
        // Note: this launches the worker.
        const worker = this.#args.initWorker();
        const { remote: initializeWorker, dispose } = ComlinkWrap(worker);
        this.#disposeRemote = dispose;
        this.#sourceWorkerRemote = await initializeWorker(this.#args.initArgs);
        return await this.#sourceWorkerRemote.initialize();
    }
    async *messageIterator(args) {
        if (this.#sourceWorkerRemote == undefined) {
            throw new Error(`WorkerIterableSource is not initialized`);
        }
        const cursor = this.getMessageCursor(args);
        try {
            for (;;) {
                // The fastest framerate that studio renders at is 60fps. So to render a frame studio needs
                // at minimum ~16 milliseconds of messages before it will render a frame. Here we fetch
                // batches of 17 milliseconds so that one batch fetch could result in one frame render.
                // Fetching too much in a batch means we cannot render until the batch is returned.
                const results = await cursor.nextBatch(17 /* milliseconds */);
                if (!results || results.length === 0) {
                    break;
                }
                yield* results;
            }
        }
        finally {
            await cursor.end();
        }
    }
    async getBackfillMessages(args) {
        if (this.#sourceWorkerRemote == undefined) {
            throw new Error(`WorkerIterableSource is not initialized`);
        }
        // An AbortSignal is not clonable, so we remove it from the args and send it as a separate argumet
        // to our worker getBackfillMessages call. Our installed Comlink handler for AbortSignal handles
        // making the abort signal available within the worker.
        const { abortSignal, ...rest } = args;
        return await this.#sourceWorkerRemote.getBackfillMessages(rest, abortSignal);
    }
    getMessageCursor(args) {
        if (this.#sourceWorkerRemote == undefined) {
            throw new Error(`WorkerIterableSource is not initialized`);
        }
        // An AbortSignal is not clonable, so we remove it from the args and send it as a separate argumet
        // to our worker getBackfillMessages call. Our installed Comlink handler for AbortSignal handles
        // making the abort signal available within the worker.
        const { abort, ...rest } = args;
        const messageCursorPromise = this.#sourceWorkerRemote.getMessageCursor(rest, abort);
        const cursor = {
            async next() {
                const messageCursor = await messageCursorPromise;
                return await messageCursor.next();
            },
            async nextBatch(durationMs) {
                const messageCursor = await messageCursorPromise;
                return await messageCursor.nextBatch(durationMs);
            },
            async readUntil(end) {
                const messageCursor = await messageCursorPromise;
                return await messageCursor.readUntil(end);
            },
            async end() {
                const messageCursor = await messageCursorPromise;
                try {
                    await messageCursor.end();
                }
                finally {
                    messageCursor[Comlink.releaseProxy]();
                }
            },
        };
        return cursor;
    }
    async terminate() {
        this.#disposeRemote?.();
        // shouldn't normally have to do this, but if `initialize` is called after again we don't want
        // to reuse the old remote
        this.#disposeRemote = undefined;
        this.#sourceWorkerRemote = undefined;
    }
}
