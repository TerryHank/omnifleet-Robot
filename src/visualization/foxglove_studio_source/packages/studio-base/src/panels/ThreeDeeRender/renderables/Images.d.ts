import { SettingsTreeAction } from "@foxglove/studio";
import { ImageRenderable, ImageUserData } from "./Images/ImageRenderable";
import { AnyImage } from "./Images/ImageTypes";
import type { AnyRendererSubscription, IRenderer } from "../IRenderer";
import { PartialMessageEvent, SceneExtension } from "../SceneExtension";
import { SettingsTreeEntry } from "../SettingsManager";
import { BaseSettings } from "../settings";
export type LayerSettingsImage = BaseSettings & {
    cameraInfoTopic: string | undefined;
    distance: number;
    planarProjectionFactor: number;
    color: string;
};
export declare class Images extends SceneExtension<ImageRenderable> {
    #private;
    static extensionId: string;
    protected supportedImageSchemas: Set<string>;
    constructor(renderer: IRenderer, name?: string);
    dispose(): void;
    getSubscriptions(): readonly AnyRendererSubscription[];
    settingsNodes(): SettingsTreeEntry[];
    handleSettingsAction: (action: SettingsTreeAction) => void;
    protected handleImage: (messageEvent: PartialMessageEvent<AnyImage>, image: AnyImage) => void;
    protected initRenderable(topicName: string, userData: ImageUserData): ImageRenderable;
}
