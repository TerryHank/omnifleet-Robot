// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
/**
 * Class for storing a single instance of each geometry to reuse across scene extensions
 * Callers of `getGeometry` will need to specify a unique key from which to extract the
 * singleton geometry.
 */
export class SharedGeometry {
    #geometryMap = new Map();
    /**
     * Get a geometry from the map, or create it if it doesn't exist.
     * Note that this map will not allow overwriting of existing geometries.
     * @param key unique key to identify the geometry
     * @param createGeometry - function to create the geometry if it does not exist
     * @returns - created geometry if it doesn't exist or the existing geometry from the map
     */
    getGeometry(key, createGeometry) {
        let geometry = this.#geometryMap.get(key);
        if (!geometry) {
            geometry = createGeometry();
            this.#geometryMap.set(key, geometry);
        }
        return geometry;
    }
    // disposes of all geometries and clears the map
    dispose() {
        for (const geometry of this.#geometryMap.values()) {
            geometry.dispose();
        }
        this.#geometryMap.clear();
    }
}
