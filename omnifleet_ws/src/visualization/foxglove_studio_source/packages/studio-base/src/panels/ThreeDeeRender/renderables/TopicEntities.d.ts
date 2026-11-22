import { SceneEntity, SceneEntityDeletion } from "@foxglove/schemas";
import { PrimitivePool } from "./primitives/PrimitivePool";
import type { IRenderer } from "../IRenderer";
import { BaseUserData, Renderable } from "../Renderable";
import { LayerSettingsEntity } from "../settings";
export type EntityTopicUserData = BaseUserData & {
    topic: string;
    settings: LayerSettingsEntity;
};
export declare class TopicEntities extends Renderable<EntityTopicUserData> {
    #private;
    private primitivePool;
    pickable: boolean;
    constructor(name: string, primitivePool: PrimitivePool, renderer: IRenderer, userData: EntityTopicUserData);
    dispose(): void;
    updateSettings(): void;
    setColorScheme(colorScheme: "dark" | "light"): void;
    startFrame(currentTime: bigint, renderFrameId: string, fixedFrameId: string): void;
    addOrUpdateEntity(entity: SceneEntity, receiveTime: bigint): void;
    deleteEntities(deletion: SceneEntityDeletion): void;
}
