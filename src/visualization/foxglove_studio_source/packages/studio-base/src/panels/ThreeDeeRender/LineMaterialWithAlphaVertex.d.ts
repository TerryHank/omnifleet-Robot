/**
 * parameters = {
 *  color: <hex>,
 *  linewidth: <float>,
 *  dashed: <boolean>,
 *  dashScale: <float>,
 *  dashSize: <float>,
 *  dashOffset: <float>,
 *  gapSize: <float>,
 *  resolution: <Vector2>, // to be set by renderer
 * }
 */
import { ShaderMaterial, Vector2, MaterialParameters } from "three";
export interface LineMaterialParameters extends MaterialParameters {
    alphaToCoverage?: boolean | undefined;
    color?: number | undefined;
    dashed?: boolean | undefined;
    dashScale?: number | undefined;
    dashSize?: number | undefined;
    dashOffset?: number | undefined;
    gapSize?: number | undefined;
    linewidth?: number | undefined;
    resolution?: Vector2 | undefined;
    wireframe?: boolean | undefined;
    worldUnits?: boolean | undefined;
}
/** LineMaterial that supports vertex colors with an alpha channel */
export declare class LineMaterialWithAlphaVertex extends ShaderMaterial {
    readonly isLineMaterial = true;
    constructor(parameters: LineMaterialParameters);
    get color(): any;
    set color(value: any);
    get worldUnits(): boolean;
    set worldUnits(value: boolean);
    get lineWidth(): any;
    set lineWidth(value: any);
    get dashed(): boolean;
    set dashed(value: boolean);
    get dashScale(): any;
    set dashScale(value: any);
    get dashSize(): any;
    set dashSize(value: any);
    get dashOffset(): any;
    set dashOffset(value: any);
    get gapSize(): any;
    set gapSize(value: any);
    setOpacity(value: number): void;
    get resolution(): THREE.Vector2;
    set resolution(value: THREE.Vector2);
}
