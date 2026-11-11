import type { SettingsTreeField } from "@foxglove/studio";
export type SelectEntry = {
    label: string;
    value: string;
};
export type TwoColors = [string, string];
export type Vec3 = [number, number, number];
/**
 * Common settings for all persisted SceneExtension settings.
 */
export type BaseSettings = {
    /** Visibility for any associated scene renderables and settings tree nodes. */
    visible: boolean;
    /** If true, always use `currentTime` for pose updates. This means objects in a coordinate frame
     * will move as the coordinate frame moves. */
    frameLocked?: boolean;
};
export type LayerSettingsEntity = BaseSettings & {
    showOutlines: boolean | undefined;
    color: string | undefined;
    selectedIdVariable: string | undefined;
};
/**
 * Settings for a "Custom Layer", a user-added collection of one or more renderables such as a Grid.
 */
export type CustomLayerSettings = BaseSettings & {
    /** An identifier for a unique instance of a layer. */
    instanceId: string;
    /** An identifier for a type of layer, such as `"foxglove.Grid"`. */
    layerId: string;
    /** The label to use for this layer in the settings tree, under "Custom Layers". */
    label: string;
    /** Optional value specifying order in the custom layer list */
    order?: number;
};
export declare const PRECISION_DISTANCE = 3;
export declare const PRECISION_DEGREES = 1;
export declare function fieldSize(label: string, value: number | undefined, placeholder?: string | number): SettingsTreeField;
export declare function fieldScaleVec3(label: string, value: Vec3): SettingsTreeField;
export declare function fieldLineWidth(label: string, value: number | undefined, placeholder?: string | number): SettingsTreeField;
export declare function fieldGradient(label: string, value: TwoColors): SettingsTreeField;
