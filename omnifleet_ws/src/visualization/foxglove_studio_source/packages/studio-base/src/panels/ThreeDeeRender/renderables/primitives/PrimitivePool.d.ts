import { RenderableArrows } from "./RenderableArrows";
import { RenderableCubes } from "./RenderableCubes";
import { RenderableCylinders } from "./RenderableCylinders";
import { RenderableLines } from "./RenderableLines";
import { RenderableModels } from "./RenderableModels";
import { RenderableSpheres } from "./RenderableSpheres";
import { RenderableTexts } from "./RenderableTexts";
import { RenderableTriangles } from "./RenderableTriangles";
import { PrimitiveType } from "./types";
import type { IRenderer } from "../../IRenderer";
declare const CONSTRUCTORS: {
    CUBES: typeof RenderableCubes;
    MODELS: typeof RenderableModels;
    LINES: typeof RenderableLines;
    CYLINDERS: typeof RenderableCylinders;
    ARROWS: typeof RenderableArrows;
    SPHERES: typeof RenderableSpheres;
    TEXTS: typeof RenderableTexts;
    TRIANGLES: typeof RenderableTriangles;
};
/**
 * An object pool for RenderablePrimitive subclass objects.
 */
export declare class PrimitivePool {
    #private;
    private renderer;
    constructor(renderer: IRenderer);
    acquire<T extends PrimitiveType>(type: T): InstanceType<(typeof CONSTRUCTORS)[T]>;
    release<T extends PrimitiveType>(type: T, primitive: InstanceType<(typeof CONSTRUCTORS)[T]>): void;
    dispose(): void;
    setColorScheme(colorScheme: "dark" | "light"): void;
}
export {};
