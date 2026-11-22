// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import * as THREE from "three";
import { crc32 } from "@foxglove/crc";
import { toNanoSec } from "@foxglove/rostime";
import { RenderablePrimitive } from "./RenderablePrimitive";
import { EDGE_LINE_SEGMENTS_NAME } from "../../ModelCache";
import { makeRgba, rgbToThreeColor, stringToRgba } from "../../color";
import { disposeMeshesRecursive } from "../../dispose";
import { removeLights, replaceMaterials } from "../models";
const tempRgba = makeRgba();
const MODEL_FETCH_FAILED = "MODEL_FETCH_FAILED";
function byteArraysEqual(a, b) {
    if (a.length !== b.length) {
        return false;
    }
    for (let i = 0; i < a.length; i++) {
        if (a[i] !== b[i]) {
            return false;
        }
    }
    return true;
}
export class RenderableModels extends RenderablePrimitive {
    /** Renderables loaded from embedded data */
    #renderablesByDataCrc = new Map();
    /** Renderables loaded from URLs */
    #renderablesByUrl = new Map();
    #updateCount = 0;
    constructor(renderer) {
        super("", renderer);
    }
    /**
     * Creates a new renderable for the given primitive
     * @param primitive Primitive to instantiate renderable with
     * @param getURL Called to retrieve the URL that should be used to load the primitive
     * @param revokeURL Called with the URL returned by getURL after loading is complete
     */
    async #createRenderable(primitive, getURL, revokeURL) {
        const url = getURL(primitive);
        let renderable;
        try {
            // Load the model if necessary
            const cachedModel = await this.#loadCachedModel(url, {
                overrideMediaType: primitive.media_type.length > 0 ? primitive.media_type : undefined,
            });
            if (cachedModel) {
                renderable = { model: cloneAndPrepareModel(cachedModel), cachedModel, primitive };
            }
        }
        finally {
            revokeURL(url);
        }
        return renderable;
    }
    /**
     * Uses matching function to find, remove and return the first renderable from the list that matches
     * @param renderables - (MUTABLE) list of RenderableModel objects
     * @param primitivesMatch - Comparison function that returns true if the two primitives are a match
     * @param primitive - Primitive to match against
     * @returns - matching renderable if found, otherwise undefined
     */
    #removeMatchFromList(renderables, isMatch) {
        if (renderables) {
            const idx = renderables.findIndex((prev) => isMatch(prev.primitive));
            if (idx >= 0) {
                // remove from previous renderables so that it doesn't get disposed
                return renderables.splice(idx, 1)[0];
            }
        }
        return undefined;
    }
    /**
     * Updates renderables to reflect a new list of primitives
     * @param models - list of ModelPrimitive objects to show in the next update
     */
    #updateModels(models) {
        const originalUpdateCount = ++this.#updateCount;
        const prevRenderablesByUrl = this.#renderablesByUrl;
        this.#renderablesByUrl = new Map();
        const prevRenderablesByDataCrc = this.#renderablesByDataCrc;
        this.#renderablesByDataCrc = new Map();
        const modelsToLoad = [];
        // iterate over new primitives and update existing renderables
        // add primitives that don't have models yet to modelsToLoad
        for (const primitive of models) {
            let prevRenderables;
            let newRenderables;
            let renderable;
            if (primitive.url.length === 0) {
                const dataCrc = crc32(primitive.data);
                prevRenderables = prevRenderablesByDataCrc.get(dataCrc);
                newRenderables = this.#renderablesByDataCrc.get(dataCrc);
                if (!newRenderables) {
                    newRenderables = [];
                    this.#renderablesByDataCrc.set(dataCrc, newRenderables);
                }
                renderable = this.#removeMatchFromList(prevRenderables, (model) => dataPrimitivesMatch(model, primitive));
            }
            else {
                prevRenderables = prevRenderablesByUrl.get(primitive.url);
                newRenderables = this.#renderablesByUrl.get(primitive.url);
                if (!newRenderables) {
                    newRenderables = [];
                    this.#renderablesByUrl.set(primitive.url, newRenderables);
                }
                renderable = this.#removeMatchFromList(prevRenderables, (model) => urlPrimitivesMatch(model, primitive));
            }
            // renderable not found in prevRenderables
            if (renderable) {
                this.#updateModel(renderable, primitive);
                newRenderables.push(renderable);
                this.add(renderable.model);
            }
            else {
                modelsToLoad.push(primitive);
            }
        }
        Promise.all(modelsToLoad.map(async (primitive) => {
            let newRenderables;
            let renderable;
            if (primitive.url.length === 0) {
                const dataCrc = crc32(primitive.data);
                // this should always resolve because it was created in the loop above
                newRenderables = this.#renderablesByDataCrc.get(dataCrc);
                try {
                    renderable = await this.#createRenderable(primitive, (model) => URL.createObjectURL(new Blob([model.data], { type: model.media_type })), (url) => {
                        URL.revokeObjectURL(url);
                    });
                }
                catch (err) {
                    this.renderer.settings.errors.add(this.userData.settingsPath, MODEL_FETCH_FAILED, `Unhandled error loading model from ${primitive.data.byteLength}-byte data: ${err.message}`);
                }
            }
            else {
                // this should always resolve because it was created in the loop above
                newRenderables = this.#renderablesByUrl.get(primitive.url);
                try {
                    renderable = await this.#createRenderable(primitive, (model) => model.url, (_url) => { });
                }
                catch (err) {
                    this.renderer.settings.errors.add(this.userData.settingsPath, MODEL_FETCH_FAILED, `Unhandled error loading model from "${primitive.url}": ${err.message}`);
                }
            }
            if (originalUpdateCount !== this.#updateCount) {
                // another update has come in, bail before doing any mutations
                return;
            }
            if (renderable) {
                this.#updateModel(renderable, primitive);
                newRenderables.push(renderable);
                this.add(renderable.model);
                // Render a new frame now that the model is loaded
                this.renderer.queueAnimationFrame();
            }
        }))
            .then(() => {
            // Remove any mesh fetch error message since loading was successful
            this.renderer.settings.errors.remove(this.userData.settingsPath, MODEL_FETCH_FAILED);
        })
            .catch(console.error)
            .finally(() => {
            // update for new models
            this.#updateOutlineVisibility();
        });
        // Only unused models should be left in the `prevRenderables` lists after
        // using this.#removeMatchFromList() above
        for (const renderables of prevRenderablesByUrl.values()) {
            for (const renderable of renderables) {
                renderable.model.removeFromParent();
                this.#disposeModel(renderable);
            }
        }
        for (const renderables of prevRenderablesByDataCrc.values()) {
            for (const renderable of renderables) {
                renderable.model.removeFromParent();
                this.#disposeModel(renderable);
            }
        }
        // Necessary to have this twice because we want old models be synced with outline settings before the new models load
        // update for existing models that haven't changed
        this.#updateOutlineVisibility();
    }
    dispose() {
        for (const renderables of this.#renderablesByUrl.values()) {
            for (const renderable of renderables) {
                this.#disposeModel(renderable);
            }
        }
        this.#renderablesByUrl.clear();
        for (const renderables of this.#renderablesByDataCrc.values()) {
            for (const renderable of renderables) {
                this.#disposeModel(renderable);
            }
        }
        this.#renderablesByDataCrc.clear();
    }
    update(topic, entity, settings, receiveTime) {
        super.update(topic, entity, settings, receiveTime);
        if (entity) {
            const lifetimeNs = toNanoSec(entity.lifetime);
            this.userData.expiresAt = lifetimeNs === 0n ? undefined : receiveTime + lifetimeNs;
            this.#updateModels(entity.models);
        }
    }
    updateSettings(settings) {
        this.update(this.userData.topic, this.userData.entity, settings, this.userData.receiveTime);
    }
    #updateOutlineVisibility() {
        const showOutlines = this.getSettings()?.showOutlines ?? true;
        this.traverse((lineSegments) => {
            // Want to avoid picking up the LineSegments from the model itself
            // only update line segments that we've added with the special name
            if (lineSegments instanceof THREE.LineSegments &&
                lineSegments.name === EDGE_LINE_SEGMENTS_NAME) {
                lineSegments.visible = showOutlines;
            }
        });
    }
    async #loadCachedModel(url, opts) {
        const cachedModel = await this.renderer.modelCache.load(url, { overrideMediaType: opts.overrideMediaType }, (err) => {
            this.renderer.settings.errors.add(this.userData.settingsPath, MODEL_FETCH_FAILED, `Error loading model from "${url}": ${err.message}`);
        });
        if (!cachedModel) {
            if (!this.renderer.settings.errors.hasError(this.userData.settingsPath, MODEL_FETCH_FAILED)) {
                this.renderer.settings.errors.add(this.userData.settingsPath, MODEL_FETCH_FAILED, `Failed to load model from "${url}"`);
            }
            return undefined;
        }
        return cachedModel;
    }
    #updateModel(renderable, primitive) {
        const overrideColor = this.userData.settings.color
            ? stringToRgba(tempRgba, this.userData.settings.color)
            : primitive.override_color
                ? primitive.color
                : undefined;
        if (overrideColor) {
            if (!renderable.material) {
                renderable.material = new THREE.MeshStandardMaterial({
                    metalness: 0,
                    roughness: 1,
                    dithering: true,
                });
                replaceMaterials(renderable.model, renderable.material);
            }
            rgbToThreeColor(renderable.material.color, overrideColor);
            const transparent = overrideColor.a < 1;
            renderable.material.opacity = overrideColor.a;
            renderable.material.transparent = transparent;
            renderable.material.depthWrite = !transparent;
            renderable.material.needsUpdate = true;
        }
        else if (renderable.material) {
            // We already discarded the original materials, need to re-clone them from the original model
            renderable.model = cloneAndPrepareModel(renderable.cachedModel);
            renderable.material = undefined;
        }
        renderable.model.scale.set(primitive.scale.x, primitive.scale.y, primitive.scale.z);
        renderable.model.position.set(primitive.pose.position.x, primitive.pose.position.y, primitive.pose.position.z);
        renderable.model.quaternion.set(primitive.pose.orientation.x, primitive.pose.orientation.y, primitive.pose.orientation.z, primitive.pose.orientation.w);
    }
    #disposeModel(renderable) {
        renderable.material?.dispose();
        disposeMeshesRecursive(renderable.model);
        disposeMeshesRecursive(renderable.cachedModel);
    }
}
function cloneAndPrepareModel(cachedModel) {
    const model = cachedModel.clone(true);
    removeLights(model);
    return new THREE.Group().add(model);
}
/** Used to check that data primitives are using the same model data */
const dataPrimitivesMatch = (model1, model2) => model1.media_type === model2.media_type && byteArraysEqual(model1.data, model2.data);
/** Used to check that url-data primitives are using the same model data */
const urlPrimitivesMatch = (model1, model2) => model1.url === model2.url && model1.media_type === model2.media_type;
