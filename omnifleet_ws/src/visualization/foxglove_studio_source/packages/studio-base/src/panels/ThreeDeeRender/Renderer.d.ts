import EventEmitter from "eventemitter3";
import * as THREE from "three";
import { Immutable, MessageEvent, ParameterValue, SettingsIcon, SettingsTreeNodeActionItem, Topic, VariableValue } from "@foxglove/studio";
import { PanelContextMenuItem } from "@foxglove/studio-base/components/PanelContextMenu";
import { Asset, BuiltinPanelExtensionContext, DraggedMessagePath, MessagePathDropStatus } from "@foxglove/studio-base/components/PanelExtensionAdapter";
import { HUDItemManager } from "@foxglove/studio-base/panels/ThreeDeeRender/HUDItemManager";
import { ICameraHandler } from "@foxglove/studio-base/panels/ThreeDeeRender/renderables/ICameraHandler";
import IAnalytics from "@foxglove/studio-base/services/IAnalytics";
import { LabelPool } from "@foxglove/three-text";
import { HUDItem } from "./HUDItemManager";
import { IRenderer, InstancedLineMaterial, RendererConfig, RendererEvents, RendererSubscription, TestOptions } from "./IRenderer";
import { Input } from "./Input";
import { ModelCache } from "./ModelCache";
import { PickedRenderable } from "./Picker";
import type { Renderable } from "./Renderable";
import { SceneExtension } from "./SceneExtension";
import { SceneExtensionConfig } from "./SceneExtensionConfig";
import { SettingsManager } from "./SettingsManager";
import { SharedGeometry } from "./SharedGeometry";
import { CameraState } from "./camera";
import { DetailLevel } from "./lod";
import { MeasurementTool } from "./renderables/MeasurementTool";
import { PublishClickTool } from "./renderables/PublishClickTool";
import { MarkerPool } from "./renderables/markers/MarkerPool";
import { Quaternion, Vector3 } from "./ros";
import { SelectEntry } from "./settings";
import { TransformTree } from "./transforms";
import { InterfaceMode } from "./types";
/** Menu item entry and callback for the "Custom Layers" menu */
export type CustomLayerAction = {
    action: SettingsTreeNodeActionItem;
    handler: (instanceId: string) => void;
};
/**
 * An extensible 3D renderer attached to a `HTMLCanvasElement`,
 * `WebGLRenderingContext`, and `SettingsTree`.
 */
export declare class Renderer extends EventEmitter<RendererEvents> implements IRenderer {
    #private;
    readonly interfaceMode: InterfaceMode;
    readonly gl: THREE.WebGLRenderer;
    maxLod: DetailLevel;
    debugPicking: boolean;
    config: Immutable<RendererConfig>;
    settings: SettingsManager;
    topics: ReadonlyArray<Topic> | undefined;
    topicsByName: ReadonlyMap<string, Topic> | undefined;
    parameters: ReadonlyMap<string, ParameterValue> | undefined;
    variables: ReadonlyMap<string, VariableValue>;
    sceneExtensions: Map<string, SceneExtension<Renderable<import("./Renderable").BaseUserData, IRenderer>, THREE.Object3DEventMap>>;
    schemaSubscriptions: Map<string, RendererSubscription[]>;
    topicSubscriptions: Map<string, RendererSubscription[]>;
    /** HUD manager instance */
    hud: HUDItemManager;
    /** Items to display in the HUD */
    hudItems: HUDItem[];
    input: Input;
    readonly outlineMaterial: THREE.LineBasicMaterial;
    readonly instancedOutlineMaterial: InstancedLineMaterial;
    /** only public for testing - prefer to use `getCameraState` instead */
    cameraHandler: ICameraHandler;
    measurementTool: MeasurementTool;
    publishClickTool: PublishClickTool;
    ros: boolean;
    colorScheme: "dark" | "light";
    modelCache: ModelCache;
    transformTree: TransformTree;
    coordinateFrameList: SelectEntry[];
    currentTime: bigint;
    fixedFrameId: string | undefined;
    followFrameId: string | undefined;
    labelPool: LabelPool;
    markerPool: MarkerPool;
    sharedGeometry: SharedGeometry;
    readonly displayTemporaryError?: (str: string) => void;
    /** Options passed for local testing and storybook. */
    readonly testOptions: TestOptions;
    analytics?: IAnalytics;
    constructor(args: {
        canvas: HTMLCanvasElement;
        config: Immutable<RendererConfig>;
        interfaceMode: InterfaceMode;
        sceneExtensionConfig: SceneExtensionConfig;
        fetchAsset: BuiltinPanelExtensionContext["unstable_fetchAsset"];
        displayTemporaryError?: (message: string) => void;
        testOptions: TestOptions;
    });
    dispose(): void;
    cameraSyncError(): undefined | string;
    setCameraSyncError(error: undefined | string): void;
    getPixelRatio(): number;
    /**
     *
     * @param currentTime what renderer.currentTime will be set to
     */
    setCurrentTime(newTimeNs: bigint): void;
    /**
     * Updates renderer state according to seek delta. Handles clearing of future state and resetting of allFrames cursor if seeked backwards
     * Should be called after `setCurrentTime` as been called
     * @param oldTime used to determine if seeked backwards
     */
    handleSeek(oldTimeNs: bigint): void;
    /**
     * Clears:
     *  - Rendered objects (a backfill is performed to ensure that they are regenerated with new messages from current frame)
     *  - Errors in settings. Messages that caused errors in the past are cleared, but will be re-added if they are still causing errors when read in.
     *  - [Optional] Transform tree. This should be set to true when a seek to a previous time is performed in order to flush potential future state to the newly set time.
     *  - [Optional] allFramesCursor. This is the cursor that iterates through allFrames up to currentTime. It should be reset when seeking backwards to avoid keeping future state.
     * @param {Object} params - modifiers to the clear operation
     * @param {boolean} params.clearTransforms - whether to clear the transform tree. This should be set to true when a seek to a previous time is performed in order
     * order to flush potential future state to the newly set time.
     * @param {boolean} params.resetAllFramesCursor - whether to reset the cursor for the allFrames array.
     * Order to clear ImageMode renderables or not. Defaults to true. Not relevant in 3D panel.
     * @param {boolean} params.clearImageModeExtension - whether to reset ImageMode renderables in clear.
     */
    clear({ clearTransforms, resetAllFramesCursor, clearImageModeExtension, }?: {
        clearTransforms?: boolean;
        resetAllFramesCursor?: boolean;
        clearImageModeExtension?: boolean;
    }): void;
    /**
     * Iterates through allFrames and handles messages with a receiveTime <= currentTime
     * @param allFrames - sorted array of all preloaded messages
     * @returns {boolean} - whether the allFramesCursor has been updated and new messages were read in
     */
    handleAllFramesMessages(allFrames?: readonly MessageEvent[]): boolean;
    updateConfig(updateHandler: (draft: RendererConfig) => void): void;
    /**
     * Image Only mode disables all subscriptions for non-ImageMode scene extensions and clears all transform subscriptions.
     * This mode should only be enabled in ImageMode when there is no calibration topic selected. Disabling these subscriptions
     * prevents the 3D aspects of the scene from being rendered from an insufficient camera info.
     */
    enableImageOnlySubscriptionMode: () => void;
    disableImageOnlySubscriptionMode: () => void;
    addCustomLayerAction(options: {
        layerId: string;
        label: string;
        icon?: SettingsIcon;
        handler: (instanceId: string) => void;
    }): void;
    /** Enable or disable object selection mode */
    setPickingEnabled(enabled: boolean): void;
    /** Update the color scheme and background color, rebuilding any materials as necessary */
    setColorScheme(colorScheme: "dark" | "light", backgroundColor: string | undefined): void;
    /** Update the list of topics and rebuild all settings nodes when the identity
     * of the topics list changes */
    setTopics(topics: ReadonlyArray<Topic> | undefined): void;
    setParameters(parameters: ReadonlyMap<string, ParameterValue> | undefined): void;
    updateCustomLayersCount(): void;
    setCameraState(cameraState: CameraState): void;
    getCameraState(): CameraState | undefined;
    canResetView(): boolean;
    resetView(): void;
    setSelectedRenderable(selection: PickedRenderable | undefined): void;
    addMessageEvent(messageEvent: Readonly<MessageEvent>): void;
    /** Match the behavior of `tf::Transformer` by stripping leading slashes from
     * frame_ids. This preserves compatibility with earlier versions of ROS while
     * not breaking any current versions where:
     * > tf2 does not accept frame_ids starting with "/"
     * Source: <http://wiki.ros.org/tf2/Migration#tf_prefix_backwards_compatibility>
     */
    normalizeFrameId(frameId: string): string;
    addCoordinateFrame(frameId: string): void;
    addTransform(parentFrameId: string, childFrameId: string, stamp: bigint, translation: Vector3, rotation: Quaternion, errorSettingsPath?: string[]): void;
    removeTransform(childFrameId: string, parentFrameId: string, stamp: bigint): void;
    animationFrame: () => void;
    queueAnimationFrame(): void;
    setFollowFrameId(frameId: string | undefined): void;
    fetchAsset(uri: string, options?: {
        signal?: AbortSignal;
        baseUrl?: string;
    }): Promise<Asset>;
    getContextMenuItems: () => PanelContextMenuItem[];
    getDropStatus: (paths: readonly DraggedMessagePath[]) => MessagePathDropStatus;
    handleDrop: (paths: readonly DraggedMessagePath[]) => void;
    setAnalytics(analytics: IAnalytics): void;
}
