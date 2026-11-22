// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { ComlinkWrap } from "@foxglove/den/worker";
export class WorkerImageDecoder {
    #remote;
    #dispose;
    constructor() {
        const { remote, dispose } = ComlinkWrap(new Worker(
        // foxglove-depcheck-used: babel-plugin-transform-import-meta
        new URL("./WorkerImageDecoder.worker", import.meta.url)));
        this.#remote = remote;
        this.#dispose = dispose;
    }
    /**
     * Copies `image` to the worker, and transfers the decoded result back to the main thread.
     */
    async decode(image, options) {
        return await this.#remote.decode(image, options);
    }
    terminate() {
        this.#dispose();
    }
}
