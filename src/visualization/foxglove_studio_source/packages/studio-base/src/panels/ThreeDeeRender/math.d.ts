import * as THREE from "three";
export declare function getRotationTo(src: THREE.Vector3, dest: THREE.Vector3): THREE.Quaternion;
export declare function isZeroLength(vec: THREE.Vector3): boolean;
export declare function approxEquals(a: number, b: number, epsilon?: number): boolean;
export declare function vec3TupleApproxEquals(a: THREE.Vector3Tuple, b: THREE.Vector3Tuple, epsilon?: number): boolean;
export declare function clamp(value: number, min: number, max: number): number;
export declare function lerp(a: number, b: number, t: number): number;
