import { SceneEntity } from "@foxglove/schemas";
import { RenderablePrimitive } from "./RenderablePrimitive";
import type { IRenderer } from "../../IRenderer";
import { LayerSettingsEntity } from "../../settings";
export declare class RenderableCylinders extends RenderablePrimitive {
    #private;
    constructor(renderer: IRenderer);
    setColorScheme(colorScheme: "dark" | "light"): void;
    dispose(): void;
    update(topic: string | undefined, entity: SceneEntity | undefined, settings: LayerSettingsEntity, receiveTime: bigint): void;
    updateSettings(settings: LayerSettingsEntity): void;
}
