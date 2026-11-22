/** Render order for given annotations. Higher numbers rendered after lower numbers */
export declare const ANNOTATION_RENDER_ORDER: {
    FILL: number;
    LINE_PREPASS: number;
    LINE: number;
    POINTS: number;
    TEXT: number;
};
/** we want annotations to show on top of the entire scene. These are material props to achieve that */
export declare const annotationRenderOrderMaterialProps: {
    /** We need to set transparent to true so that transparent objects aren't rendered on top of it.
     * Transparent objects are rendered after non-transparent objects. If this were set to false or
     * set based on color of annotations, then the foreground image with opacity would be rendered on top
     * until it is fully opaque.
     */
    transparent: boolean;
    depthWrite: boolean;
    depthTest: boolean;
};
