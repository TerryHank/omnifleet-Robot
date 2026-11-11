import * as THREE from "three";
import type { RosValue } from "@foxglove/studio-base/players/types";
import type { IRenderer } from "./IRenderer";
import type { BaseSettings } from "./settings";
import type { Pose } from "./transforms";
export declare const SELECTED_ID_VARIABLE = "selected_id";
export type BaseUserData = {
    /** Timestamp when the associated `MessageEvent` was received */
    receiveTime: bigint;
    /** Timestamp extracted from a field in the associated message, such as `header.stamp` */
    messageTime: bigint;
    /** Coordinate frame this Renderable exists in */
    frameId: string;
    /** Local position and orientation of the Renderable */
    pose: Pose;
    /** Settings tree path where errors will be displayed */
    settingsPath: ReadonlyArray<string>;
    /** User-customizable settings for this Renderable */
    settings: BaseSettings;
    /** Topic that the Renderable belongs to, if applicable*/
    topic?: string;
};
/**
 * Renderables are generic THREE.js scene graph entities with additional
 * properties from `BaseUserData` that allow coordinate frame transforms to
 * automatically be applied and settings tree errors to be displayed.
 *
 * TRenderer may be set to `undefined` to opt out of access to the bloated IRenderer interface.
 */
export declare class Renderable<TUserData extends BaseUserData = BaseUserData, TRenderer extends IRenderer | undefined = IRenderer> extends THREE.Object3D {
    /** Identifies this class as inheriting from `Renderable` */
    readonly isRenderable = true;
    /** Allow this Renderable to be selected during picking and shown in the Object Details view */
    readonly pickable: boolean;
    /**
     * Use a second picking pass for this Renderable to select a single numeric instanceId. This
     * instanceId can be passed to `instanceDetails()` to get more information about the instance.
     */
    readonly pickableInstances: boolean;
    /** A reference to the parent `Renderer` that owns the scene graph containing this object */
    protected readonly renderer: TRenderer;
    /** Additional data associated with this entity */
    userData: TUserData;
    constructor(name: string, renderer: TRenderer, userData: TUserData);
    /**
     * Dispose of any unmanaged resources uniquely associated with this Renderable
     * such as GPU buffers.
     */
    dispose(): void;
    /**
     * A unique identifier for this Renderable, taken from the associated message.
     */
    idFromMessage(): number | string | undefined;
    /**
     * The name of the variable that will be set to `idFromMessage()` on user selection.
     */
    selectedIdVariable(): string | undefined;
    /**
     * Return a Plain Old JavaScript Object (POJO) representation of this Renderable.
     */
    details(): Record<string, RosValue>;
    /**
     * Return topic if one exists on the userData.
     */
    get topic(): TUserData["topic"];
    /**
     * Return pose as defined in userData
     */
    get pose(): Pose;
    /**
     * Return a Plain Old JavaScript Object (POJO) representation of a specific
     * visual instance rendered by this Renderable.
     */
    instanceDetails(instanceId: number): Record<string, RosValue> | undefined;
}
