import { SettingsTreeAction } from "@foxglove/studio";
import type { IRenderer, RendererConfig } from "../IRenderer";
import { SceneExtension } from "../SceneExtension";
import { SettingsTreeEntry } from "../SettingsManager";
export declare const DEFAULT_PUBLISH_SETTINGS: RendererConfig["publish"];
export declare class PublishSettings extends SceneExtension {
    #private;
    static extensionId: string;
    constructor(renderer: IRenderer, name?: string);
    dispose(): void;
    settingsNodes(): SettingsTreeEntry[];
    handleSettingsAction: (action: SettingsTreeAction) => void;
}
