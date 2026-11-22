import type { WebGLCapabilities } from "three";
export declare enum DetailLevel {
    Low = 0,
    Medium = 1,
    High = 2
}
/** Returns the number of samples used for Multi-Sample Anti-Aliasing (MSAA) */
export declare function msaaSamples(capabilities: WebGLCapabilities): number;
export declare function arrowShaftSubdivisions(lod: DetailLevel): number;
export declare function arrowHeadSubdivisions(lod: DetailLevel): number;
export declare function cylinderSubdivisions(lod: DetailLevel): number;
export declare function sphereSubdivisions(lod: DetailLevel): number;
