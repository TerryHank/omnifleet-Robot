// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { toNanoSec } from "@foxglove/rostime";
import { SceneEntityDeletionType } from "@foxglove/schemas";
import { ALL_PRIMITIVE_TYPES, PrimitiveType } from "./primitives/types";
import { missingTransformMessage, MISSING_TRANSFORM } from "./transforms";
import { Renderable } from "../Renderable";
import { updatePose } from "../updatePose";
const INVALID_DELETION_TYPE = "INVALID_DELETION_TYPE";
const PRIMITIVE_KEYS = {
    [PrimitiveType.CUBES]: "cubes",
    [PrimitiveType.MODELS]: "models",
    [PrimitiveType.LINES]: "lines",
    [PrimitiveType.CYLINDERS]: "cylinders",
    [PrimitiveType.ARROWS]: "arrows",
    [PrimitiveType.SPHERES]: "spheres",
    [PrimitiveType.TEXTS]: "texts",
    [PrimitiveType.TRIANGLES]: "triangles",
};
export class TopicEntities extends Renderable {
    primitivePool;
    pickable = false;
    #renderablesById = new Map();
    constructor(name, primitivePool, renderer, userData) {
        super(name, renderer, userData);
        this.primitivePool = primitivePool;
    }
    dispose() {
        this.children.length = 0;
        this.#deleteAllEntities();
    }
    updateSettings() {
        // Updates each individual primitive renderable using the current topic settings
        for (const renderables of this.#renderablesById.values()) {
            for (const renderable of Object.values(renderables)) {
                renderable.updateSettings(this.userData.settings);
            }
        }
    }
    setColorScheme(colorScheme) {
        for (const renderables of this.#renderablesById.values()) {
            for (const renderable of Object.values(renderables)) {
                renderable.setColorScheme(colorScheme);
            }
        }
    }
    startFrame(currentTime, renderFrameId, fixedFrameId) {
        this.visible = this.userData.settings.visible;
        if (!this.visible) {
            this.renderer.settings.errors.clearTopic(this.topic);
            return;
        }
        for (const renderables of this.#renderablesById.values()) {
            for (const renderable of Object.values(renderables)) {
                const entity = renderable.userData.entity;
                if (!entity) {
                    continue;
                }
                // Check if this entity has expired
                const expiresAt = renderable.userData.expiresAt;
                if (expiresAt != undefined && currentTime > expiresAt) {
                    this.#deleteEntity(entity.id);
                    break;
                }
                const frameId = this.renderer.normalizeFrameId(entity.frame_id);
                const srcTime = entity.frame_locked ? currentTime : toNanoSec(entity.timestamp);
                const updated = updatePose(renderable, this.renderer.transformTree, renderFrameId, fixedFrameId, frameId, currentTime, srcTime);
                renderable.visible = updated;
                const topic = this.userData.topic;
                if (!updated) {
                    const message = missingTransformMessage(renderFrameId, fixedFrameId, frameId);
                    this.renderer.settings.errors.addToTopic(topic, MISSING_TRANSFORM, message);
                }
                else {
                    this.renderer.settings.errors.removeFromTopic(topic, MISSING_TRANSFORM);
                }
            }
        }
    }
    addOrUpdateEntity(entity, receiveTime) {
        let renderables = this.#renderablesById.get(entity.id);
        if (!renderables) {
            renderables = {};
            this.#renderablesById.set(entity.id, renderables);
        }
        for (const primitiveType of ALL_PRIMITIVE_TYPES) {
            const hasPrimitives = entity[PRIMITIVE_KEYS[primitiveType]].length > 0;
            let renderable = renderables[primitiveType];
            if (hasPrimitives) {
                if (!renderable) {
                    renderable = this.primitivePool.acquire(primitiveType);
                    renderable.name = `${entity.id}:${primitiveType} on ${this.topic}`;
                    renderable.userData.settingsPath = this.userData.settingsPath;
                    renderable.setColorScheme(this.renderer.colorScheme);
                    // @ts-expect-error TS doesn't know that renderable matches primitiveType
                    renderables[primitiveType] = renderable;
                    this.add(renderable);
                }
                renderable.update(this.userData.topic, entity, this.userData.settings, receiveTime);
            }
            else if (renderable) {
                this.remove(renderable);
                delete renderables[primitiveType];
                this.primitivePool.release(primitiveType, renderable);
            }
        }
    }
    deleteEntities(deletion) {
        switch (deletion.type) {
            case SceneEntityDeletionType.MATCHING_ID:
                this.#deleteEntity(deletion.id);
                break;
            case SceneEntityDeletionType.ALL:
                this.#deleteAllEntities();
                break;
            default:
                // Unknown action
                this.renderer.settings.errors.addToTopic(this.topic, INVALID_DELETION_TYPE, `Invalid deletion type ${deletion.type}`);
        }
    }
    #removeRenderables(renderables) {
        for (const [primitiveType, primitive] of Object.entries(renderables)) {
            if (primitive) {
                this.remove(primitive);
                this.primitivePool.release(primitiveType, primitive);
            }
        }
    }
    #deleteEntity(id) {
        const renderables = this.#renderablesById.get(id);
        if (renderables) {
            this.#removeRenderables(renderables);
        }
        this.#renderablesById.delete(id);
    }
    #deleteAllEntities() {
        for (const renderables of this.#renderablesById.values()) {
            this.#removeRenderables(renderables);
        }
        this.#renderablesById.clear();
    }
}
