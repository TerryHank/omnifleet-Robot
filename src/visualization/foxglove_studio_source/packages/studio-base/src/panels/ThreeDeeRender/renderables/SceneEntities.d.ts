import { SettingsTreeAction } from "@foxglove/studio";
import { TopicEntities } from "./TopicEntities";
import type { AnyRendererSubscription, IRenderer } from "../IRenderer";
import { SceneExtension } from "../SceneExtension";
import { SettingsTreeEntry } from "../SettingsManager";
export declare class FoxgloveSceneEntities extends SceneExtension<TopicEntities> {
    #private;
    static extensionId: string;
    constructor(renderer: IRenderer, name?: string);
    getSubscriptions(): readonly AnyRendererSubscription[];
    settingsNodes(): SettingsTreeEntry[];
    startFrame(currentTime: bigint, renderFrameId: string, fixedFrameId: string): void;
    setColorScheme(colorScheme: "dark" | "light", _backgroundColor: THREE.Color | undefined): void;
    handleSettingsAction: (action: SettingsTreeAction) => void;
    dispose(): void;
}
