// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import * as THREE from "three";
import { RenderableMarker } from "./RenderableMarker";
import { markerHasTransparency, makePointsMaterial } from "./materials";
import { DynamicBufferGeometry } from "../../DynamicBufferGeometry";
export class RenderablePoints extends RenderableMarker {
    #geometry;
    #points;
    constructor(topic, marker, receiveTime, renderer) {
        super(topic, marker, receiveTime, renderer);
        this.#geometry = new DynamicBufferGeometry();
        this.#geometry.createAttribute("position", Float32Array, 3);
        this.#geometry.createAttribute("color", Uint8Array, 4, true);
        this.#points = new THREE.Points(this.#geometry, makePointsMaterial(marker));
        this.add(this.#points);
        this.update(marker, receiveTime);
    }
    dispose() {
        this.#points.material.dispose();
    }
    update(newMarker, receiveTime) {
        const prevMarker = this.userData.marker;
        super.update(newMarker, receiveTime);
        const marker = this.userData.marker;
        const transparent = markerHasTransparency(marker);
        if (transparent !== markerHasTransparency(prevMarker)) {
            this.#points.material.transparent = transparent;
            this.#points.material.depthWrite = !transparent;
            this.#points.material.needsUpdate = true;
        }
        this.#points.material.size = marker.scale.x;
        const pointsLength = marker.points.length;
        this.#geometry.resize(pointsLength);
        this.#setPositions(marker, pointsLength);
        this.#setColors(marker, pointsLength);
    }
    #setPositions(marker, pointsLength) {
        const attribute = this.#geometry.getAttribute("position");
        const positions = attribute.array;
        for (let i = 0; i < pointsLength; i++) {
            const point = marker.points[i];
            positions[i * 3 + 0] = point.x;
            positions[i * 3 + 1] = point.y;
            positions[i * 3 + 2] = point.z;
        }
        attribute.needsUpdate = true;
    }
    #setColors(marker, pointsLength) {
        // Converts color-per-point to a flattened typed array
        const attribute = this.#geometry.getAttribute("color");
        const rgbaData = attribute.array;
        this._markerColorsToLinear(marker, pointsLength, (color, i) => {
            rgbaData[4 * i + 0] = (color[0] * 255) | 0;
            rgbaData[4 * i + 1] = (color[1] * 255) | 0;
            rgbaData[4 * i + 2] = (color[2] * 255) | 0;
            rgbaData[4 * i + 3] = (color[3] * 255) | 0;
        });
        attribute.needsUpdate = true;
    }
}
