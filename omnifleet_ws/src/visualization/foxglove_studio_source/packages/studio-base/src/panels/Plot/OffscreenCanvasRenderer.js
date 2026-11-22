// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import * as Comlink from "comlink";
import { ComlinkWrap } from "@foxglove/den/worker";
// If the datasets builder is garbage collected we also need to cleanup the worker
// This registry ensures the worker is cleaned up when the builder is garbage collected
const registry = new FinalizationRegistry((dispose) => {
    dispose();
});
export class OffscreenCanvasRenderer {
    #canvas;
    #remote;
    #theme;
    constructor(canvas, theme) {
        this.#theme = theme;
        this.#canvas = canvas;
        const worker = new Worker(
        // foxglove-depcheck-used: babel-plugin-transform-import-meta
        new URL("./ChartRenderer.worker", import.meta.url));
        const { remote, dispose } = ComlinkWrap(worker);
        // Set the promise without await so init creates only one instance of renderer even if called
        // twice.
        this.#remote = remote.init(Comlink.transfer({
            canvas: this.#canvas,
            devicePixelRatio: window.devicePixelRatio,
            gridColor: this.#theme.palette.divider,
            tickColor: this.#theme.palette.text.secondary,
        }, [this.#canvas]));
        registry.register(this, dispose);
    }
    async update(action) {
        return await (await this.#remote).update(action);
    }
    async getElementsAtPixel(pixel) {
        return await (await this.#remote).getElementsAtPixel(pixel);
    }
    async updateDatasets(datasets) {
        return await (await this.#remote).updateDatasets(datasets);
    }
}
