// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import * as THREE from "three";
export const SELECTED_ID_VARIABLE = "selected_id";
/**
 * Renderables are generic THREE.js scene graph entities with additional
 * properties from `BaseUserData` that allow coordinate frame transforms to
 * automatically be applied and settings tree errors to be displayed.
 *
 * TRenderer may be set to `undefined` to opt out of access to the bloated IRenderer interface.
 */
export class Renderable extends THREE.Object3D {
    /** Identifies this class as inheriting from `Renderable` */
    isRenderable = true;
    /** Allow this Renderable to be selected during picking and shown in the Object Details view */
    pickable = true;
    /**
     * Use a second picking pass for this Renderable to select a single numeric instanceId. This
     * instanceId can be passed to `instanceDetails()` to get more information about the instance.
     */
    pickableInstances = false;
    /** A reference to the parent `Renderer` that owns the scene graph containing this object */
    renderer;
    /** Additional data associated with this entity */
    userData;
    constructor(name, renderer, userData) {
        super();
        this.name = name;
        this.renderer = renderer;
        this.userData = userData;
    }
    /**
     * Dispose of any unmanaged resources uniquely associated with this Renderable
     * such as GPU buffers.
     */
    dispose() {
        this.children.length = 0;
    }
    /**
     * A unique identifier for this Renderable, taken from the associated message.
     */
    idFromMessage() {
        return undefined;
    }
    /**
     * The name of the variable that will be set to `idFromMessage()` on user selection.
     */
    selectedIdVariable() {
        return undefined;
    }
    /**
     * Return a Plain Old JavaScript Object (POJO) representation of this Renderable.
     */
    details() {
        return {};
    }
    /**
     * Return topic if one exists on the userData.
     */
    // eslint-disable-next-line no-restricted-syntax
    get topic() {
        return this.userData.topic;
    }
    /**
     * Return pose as defined in userData
     */
    // eslint-disable-next-line no-restricted-syntax
    get pose() {
        return this.userData.pose;
    }
    /**
     * Return a Plain Old JavaScript Object (POJO) representation of a specific
     * visual instance rendered by this Renderable.
     */
    instanceDetails(instanceId) {
        void instanceId;
        return undefined;
    }
}
