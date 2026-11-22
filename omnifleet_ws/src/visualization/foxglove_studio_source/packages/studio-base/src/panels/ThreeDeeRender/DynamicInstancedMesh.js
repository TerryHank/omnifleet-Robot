// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import * as THREE from "three";
const INITIAL_CAPACITY = 4;
const tempMat4 = new THREE.Matrix4();
/**
 * Extends InstancedMesh with a set() method that takes a list of points and
 * colors and dynamically resizes the buffer attributes.
 */
export class DynamicInstancedMesh extends THREE.InstancedMesh {
    // Total size of the buffer attributes, which can be larger than .count (instances in use)
    #capacity;
    constructor(geometry, material, initialCapacity = INITIAL_CAPACITY) {
        super(geometry, material, 0);
        this.#capacity = initialCapacity;
        this.frustumCulled = false;
        this.#resize();
    }
    set(points, scale, colors, defaultColor) {
        const count = points.length;
        this.#setCount(count);
        const colorArray = this.instanceColor.array;
        for (let i = 0; i < count; i++) {
            const point = points[i];
            const color = colors[i] ?? defaultColor;
            tempMat4.makeTranslation(point.x, point.y, point.z);
            tempMat4.scale(scale);
            this.setMatrixAt(i, tempMat4);
            colorArray[i * 3 + 0] = (color.r * 255) | 0;
            colorArray[i * 3 + 1] = (color.g * 255) | 0;
            colorArray[i * 3 + 2] = (color.b * 255) | 0;
        }
        this.instanceMatrix.needsUpdate = true;
        if (this.instanceColor) {
            this.instanceColor.needsUpdate = true;
        }
    }
    #setCount(count) {
        while (count >= this.#capacity) {
            this.#expand();
        }
        this.count = count;
    }
    #expand() {
        this.#capacity = this.#capacity + Math.trunc(this.#capacity / 2) + 16;
        this.#resize();
    }
    #resize() {
        const oldMatrixArray = this.instanceMatrix.array;
        const oldColorArray = this.instanceColor?.array;
        const newMatrixArray = new Float32Array(this.#capacity * 16);
        const newColorArray = new Uint8ClampedArray(this.#capacity * 3);
        if (oldMatrixArray.length > 0) {
            newMatrixArray.set(oldMatrixArray);
        }
        if (oldColorArray && oldColorArray.length > 0) {
            newColorArray.set(oldColorArray);
        }
        this.instanceMatrix = new THREE.InstancedBufferAttribute(newMatrixArray, 16);
        this.instanceColor = new THREE.InstancedBufferAttribute(newColorArray, 3, true);
        this.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
        this.instanceColor.setUsage(THREE.DynamicDrawUsage);
    }
}
