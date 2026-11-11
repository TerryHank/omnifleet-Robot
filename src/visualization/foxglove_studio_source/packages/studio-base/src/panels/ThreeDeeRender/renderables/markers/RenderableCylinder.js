// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import * as THREE from "three";
import { RenderableMarker } from "./RenderableMarker";
import { makeStandardMaterial } from "./materials";
import { rgbToThreeColor } from "../../color";
import { cylinderSubdivisions } from "../../lod";
export class RenderableCylinder extends RenderableMarker {
    #mesh;
    #outline;
    constructor(topic, marker, receiveTime, renderer) {
        super(topic, marker, receiveTime, renderer);
        // Cylinder mesh
        const material = makeStandardMaterial(marker.color);
        const cylinderGeometry = renderer.sharedGeometry.getGeometry(`${this.constructor.name}-cylinder-${renderer.maxLod}`, () => createGeometry(renderer.maxLod));
        this.#mesh = new THREE.Mesh(cylinderGeometry, material);
        this.#mesh.castShadow = true;
        this.#mesh.receiveShadow = true;
        this.add(this.#mesh);
        // Cylinder outline
        const edgesGeometry = renderer.sharedGeometry.getGeometry(`${this.constructor.name}-edges-${renderer.maxLod}`, () => createEdgesGeometry(cylinderGeometry));
        this.#outline = new THREE.LineSegments(edgesGeometry, renderer.outlineMaterial);
        this.#outline.userData.picking = false;
        this.#mesh.add(this.#outline);
        this.update(marker, receiveTime);
    }
    dispose() {
        this.#mesh.material.dispose();
    }
    update(newMarker, receiveTime) {
        super.update(newMarker, receiveTime);
        const marker = this.userData.marker;
        const transparent = marker.color.a < 1;
        if (transparent !== this.#mesh.material.transparent) {
            this.#mesh.material.transparent = transparent;
            this.#mesh.material.depthWrite = !transparent;
            this.#mesh.material.needsUpdate = true;
        }
        this.#outline.visible = this.getSettings()?.showOutlines ?? true;
        rgbToThreeColor(this.#mesh.material.color, marker.color);
        this.#mesh.material.opacity = marker.color.a;
        this.scale.set(marker.scale.x, marker.scale.y, marker.scale.z);
    }
}
function createGeometry(lod) {
    const subdivisions = cylinderSubdivisions(lod);
    const cylinderGeometry = new THREE.CylinderGeometry(0.5, 0.5, 1, subdivisions);
    cylinderGeometry.rotateX(Math.PI / 2); // Make the cylinder geometry stand upright
    cylinderGeometry.computeBoundingSphere();
    return cylinderGeometry;
}
function createEdgesGeometry(geometry) {
    const cylinderEdgesGeometry = new THREE.EdgesGeometry(geometry, 40);
    cylinderEdgesGeometry.computeBoundingSphere();
    return cylinderEdgesGeometry;
}
