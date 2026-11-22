import * as THREE from "three";
type TypedArrayConstructor<T extends THREE.TypedArray> = new (length: number) => T;
export declare class DynamicBufferGeometry extends THREE.BufferGeometry {
    #private;
    attributes: {
        [name: string]: THREE.BufferAttribute;
    };
    constructor(usage?: THREE.Usage);
    setUsage(usage: THREE.Usage): void;
    createAttribute<T extends THREE.TypedArray, C extends TypedArrayConstructor<T>>(name: string, arrayConstructor: C, itemSize: number, normalized?: boolean): THREE.BufferGeometry;
    resize(itemCount: number): void;
}
export {};
