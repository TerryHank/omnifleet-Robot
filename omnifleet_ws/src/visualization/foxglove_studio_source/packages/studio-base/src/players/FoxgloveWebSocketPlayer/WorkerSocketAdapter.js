// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
export default class WorkerSocketAdapter {
    #worker;
    #connectionClosed = false;
    binaryType = "";
    protocol = "";
    onerror = undefined;
    onopen = undefined;
    onclose = undefined;
    onmessage = undefined;
    constructor(wsUrl, protocols) {
        // foxglove-depcheck-used: babel-plugin-transform-import-meta
        this.#worker = new Worker(new URL("./worker", import.meta.url));
        this.#sendToWorker({ type: "open", data: { wsUrl, protocols } });
        this.#worker.onerror = (ev) => {
            if (this.onerror) {
                this.onerror(ev);
            }
        };
        this.#worker.onmessage = (event) => {
            switch (event.data.type) {
                case "open":
                    if (this.onopen) {
                        this.protocol = event.data.protocol;
                        this.onopen(event.data);
                    }
                    break;
                case "close":
                    // websocket connection got closed, we can terminate the worker
                    this.#connectionClosed = true;
                    this.#worker.terminate();
                    if (this.onclose) {
                        this.onclose(event.data);
                    }
                    break;
                case "error":
                    if (this.onerror) {
                        this.onerror(event.data);
                    }
                    break;
                case "message":
                    if (this.onmessage) {
                        this.onmessage(event.data);
                    }
                    break;
            }
        };
    }
    close() {
        if (!this.#connectionClosed) {
            this.#sendToWorker({
                type: "close",
                data: undefined,
            });
        }
    }
    send(data) {
        this.#sendToWorker({ type: "data", data });
    }
    #sendToWorker(msg) {
        if (this.#connectionClosed) {
            throw Error("Can't send message over closed websocket connection");
        }
        this.#worker.postMessage(msg);
    }
}
