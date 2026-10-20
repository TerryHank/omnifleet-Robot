import * as THREE from "three";
import { TransformTree, AnyFrameId } from "./transforms";
export declare function updatePose(renderable: THREE.Object3D, transformTree: TransformTree, renderFrameId: AnyFrameId, fixedFrameId: AnyFrameId, srcFrameId: string, dstTime: bigint, srcTime: bigint): boolean;
