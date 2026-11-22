// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import * as THREE from "three";
export class DynamicBufferGeometry extends THREE.BufferGeometry {
    attributes = {};
    #attributeConstructors = new Map();
    #usage;
    #itemCapacity = 0;
    constructor(usage = THREE.DynamicDrawUsage) {
        super();
        this.#usage = usage;
    }
    setUsage(usage) {
        this.#usage = usage;
        for (const attribute of Object.values(this.attributes)) {
            attribute.setUsage(usage);
        }
    }
    createAttribute(name, arrayConstructor, itemSize, 
    // eslint-disable-next-line @foxglove/no-boolean-parameters
    normalized) {
        const data = new arrayConstructor(this.#itemCapacity * itemSize);
        const attribute = new THREE.BufferAttribute(data, itemSize, normalized);
        attribute.setUsage(this.#usage);
        this.#attributeConstructors.set(name, arrayConstructor);
        return this.setAttribute(name, attribute);
    }
    resize(itemCount) {
        this.setDrawRange(0, itemCount);
        if (itemCount <= this.#itemCapacity) {
            return;
        }
        for (const [attributeName, attribute] of Object.entries(this.attributes)) {
            const dataConstructor = this.#attributeConstructors.get(attributeName);
            if (!dataConstructor) {
                throw new Error(`DynamicBufferGeometry resize(${itemCount}) failed, missing data constructor for attribute "${attributeName}". Attributes must be created using createAttribute().`);
            }
            const data = new dataConstructor(itemCount * attribute.itemSize);
            const newAttrib = new THREE.BufferAttribute(data, attribute.itemSize, attribute.normalized);
            newAttrib.setUsage(this.#usage);
            this.setAttribute(attributeName, newAttrib);
        }
        this.#itemCapacity = itemCount;
    }
}
