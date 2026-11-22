import * as THREE from "three";
import { ColorRGB, ColorRGBA } from "./ros";
export declare const LIGHT_OUTLINE: THREE.Color;
export declare const DARK_OUTLINE: THREE.Color;
export declare function SRGBToLinear(c: number): number;
export declare function stringToRgba(output: ColorRGBA, colorStr: string): ColorRGBA;
export declare function makeRgba(): ColorRGBA;
export declare function stringToRgb<T extends ColorRGB | THREE.Color>(output: T, colorStr: string): T;
/** Converts a ColorRGB to THREE.Color and converts from sRGB to linear RGB. */
export declare function rgbToThreeColor(output: THREE.Color, rgb: ColorRGB): THREE.Color;
export declare function rgbaToCssString(color: ColorRGBA): string;
export declare function rgbaToLinear(output: ColorRGBA, color: ColorRGBA): ColorRGBA;
export declare function getLuminance(r: number, g: number, b: number): number;
/**
 * Computes a gradient step from colors `a` to `b` using pre-multiplied alpha to
 * match CSS linear gradients. The inputs are assumed to not have pre-multiplied
 * alpha, and the output will have pre-multiplied alpha.
 */
export declare function rgbaGradient(output: ColorRGBA, a: ColorRGBA, b: ColorRGBA, t: number): ColorRGBA;
