import * as THREE from "three";
/**
 * Class for storing a single instance of each geometry to reuse across scene extensions
 * Callers of `getGeometry` will need to specify a unique key from which to extract the
 * singleton geometry.
 */
export declare class SharedGeometry {
    #private;
    /**
     * Get a geometry from the map, or create it if it doesn't exist.
     * Note that this map will not allow overwriting of existing geometries.
     * @param key unique key to identify the geometry
     * @param createGeometry - function to create the geometry if it does not exist
     * @returns - created geometry if it doesn't exist or the existing geometry from the map
     */
    getGeometry<T extends THREE.BufferGeometry>(key: string, createGeometry: () => T): T;
    dispose(): void;
}
