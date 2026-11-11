// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
//
// This file incorporates work covered by the following copyright and
// permission notice:
//
//   Copyright 2019-2021 Cruise LLC
//
//   This source code is licensed under the Apache License, Version 2.0,
//   found at http://www.apache.org/licenses/LICENSE-2.0
//   You may not use this file except in compliance with the License.
import delay from "@foxglove/studio-base/util/delay";
import CachedFilelike from "./CachedFilelike";
class InMemoryFileReader {
    #buffer;
    constructor(bufferObj) {
        this.#buffer = bufferObj;
    }
    async open() {
        return { size: this.#buffer.byteLength };
    }
    fetch(offset, length) {
        if (offset + length > this.#buffer.byteLength) {
            throw new Error(`Read offset=${offset} length=${length} past buffer length ${this.#buffer.byteLength}`);
        }
        return {
            on: (type, callback) => {
                if (type === "data") {
                    setTimeout(() => {
                        callback(this.#buffer.slice(offset, offset + length));
                    }, 0);
                }
            },
            destroy() {
                // no-op
            },
        };
    }
}
const log = {
    debug: (..._args) => { },
    info: (..._args) => { },
    warn: (..._args) => { },
    error: (..._args) => { },
};
describe("CachedFilelike", () => {
    describe("#size", () => {
        it("returns the size from the underlying FileReader", async () => {
            const fileReader = new InMemoryFileReader(new Uint8Array([0, 1, 2, 3]));
            const cachedFileReader = new CachedFilelike({ fileReader, log });
            await cachedFileReader.open();
            expect(cachedFileReader.size()).toEqual(4);
        });
        it("does not throw when the size is 0", async () => {
            const fileReader = new InMemoryFileReader(new Uint8Array([]));
            const cachedFileReader = new CachedFilelike({ fileReader, log });
            await cachedFileReader.open();
            expect(cachedFileReader.size()).toEqual(0);
        });
    });
    describe("#read", () => {
        it("returns data from the underlying FileReader", async () => {
            const fileReader = new InMemoryFileReader(new Uint8Array([0, 1, 2, 3]));
            const cachedFileReader = new CachedFilelike({ fileReader, log });
            await expect(cachedFileReader.read(1, 2)).resolves.toEqual(new Uint8Array([1, 2]));
            await expect(cachedFileReader.read(2, 2)).resolves.toEqual(new Uint8Array([2, 3]));
        });
        it("returns an error in the callback if the FileReader keeps returning errors", async () => {
            const fileReader = new InMemoryFileReader(new Uint8Array([0, 1, 2, 3]));
            let interval;
            let destroyed;
            jest.spyOn(fileReader, "fetch").mockImplementation(() => {
                return {
                    on: (type, callback) => {
                        if (type === "error") {
                            interval = setInterval(() => {
                                callback(new Error("Dummy error"));
                            }, 20);
                        }
                    },
                    destroy() {
                        // eslint-disable-next-line @typescript-eslint/no-unsafe-argument
                        clearInterval(interval);
                        destroyed = true;
                    },
                };
            });
            const cachedFileReader = new CachedFilelike({ fileReader, log });
            await expect(cachedFileReader.read(1, 2)).rejects.toThrow("Dummy error");
            expect(destroyed).toEqual(true);
        });
        it("keeps reconnecting when keepReconnectingCallback is set", async () => {
            const fileReader = new InMemoryFileReader(new Uint8Array([0, 1, 2, 3]));
            let dataCallback;
            let errorCallback;
            let destroyed;
            const mockFetch = jest.spyOn(fileReader, "fetch").mockImplementation(() => {
                return {
                    on: (type, callback) => {
                        if (type === "data") {
                            dataCallback = callback;
                        }
                        if (type === "error") {
                            errorCallback = callback;
                        }
                    },
                    destroy() {
                        destroyed = true;
                    },
                };
            });
            const keepReconnectingCallback = jest.fn();
            const cachedFileReader = new CachedFilelike({ fileReader, log, keepReconnectingCallback });
            const readerPromise = cachedFileReader.read(1, 2);
            await delay(10);
            expect(mockFetch).toHaveBeenCalledTimes(1);
            if (!dataCallback || !errorCallback) {
                throw new Error("dataCallback not set");
            }
            errorCallback(new Error("Dummy error"));
            await delay(10);
            expect(keepReconnectingCallback.mock.calls).toEqual([[true]]);
            dataCallback(new Uint8Array([1, 2]));
            const data = await readerPromise;
            expect(keepReconnectingCallback.mock.calls).toEqual([[true], [false]]);
            expect([...data]).toEqual([1, 2]);
            expect(destroyed).toBe(true);
        });
        it("returns an empty buffer when requesting size 0 (does not throw an error)", async () => {
            const fileReader = new InMemoryFileReader(new Uint8Array([0, 1, 2, 3]));
            const cachedFileReader = new CachedFilelike({ fileReader, log });
            await expect(cachedFileReader.read(1, 0)).resolves.toEqual(new Uint8Array([]));
        });
    });
});
