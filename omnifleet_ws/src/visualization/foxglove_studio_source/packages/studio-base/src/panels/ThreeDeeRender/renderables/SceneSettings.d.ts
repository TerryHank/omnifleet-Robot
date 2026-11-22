import { SettingsTreeAction } from "@foxglove/studio";
import type { IRenderer } from "../IRenderer";
import { SceneExtension } from "../SceneExtension";
import { SettingsTreeEntry } from "../SettingsManager";
export declare const DEFAULT_LABEL_SCALE_FACTOR = 1;
export declare class SceneSettings extends SceneExtension {
    static extensionId: string;
    constructor(renderer: IRenderer, name?: string);
    dispose(): void;
    settingsNodes(): SettingsTreeEntry[];
    handleSettingsAction: (action: SettingsTreeAction) => void;
}
