import { SettingsTreeNode } from "@foxglove/studio";
import { BaseSettings } from "@foxglove/studio-base/panels/ThreeDeeRender/settings";
import type { ColorRGBA } from "../ros";
export type ColorConverter = (output: ColorRGBA, colorValue: number) => void;
export declare const NEEDS_MIN_MAX: string[];
export declare const colorFieldComputedPrefix = "_auto_";
export interface ColorModeSettings {
    colorMode: "flat" | "gradient" | "colormap" | "rgb" | "rgba" | "rgba-fields";
    flatColor: string;
    colorField?: string;
    gradient: [string, string];
    colorMap: "turbo" | "rainbow";
    explicitAlpha: number;
    minValue?: number;
    maxValue?: number;
}
export declare function getColorConverter<Settings extends ColorModeSettings & {
    readonly colorMode: Exclude<ColorModeSettings["colorMode"], "rgba-fields">;
}>(settings: Settings, minValue: number, maxValue: number): ColorConverter;
export declare const RGBA_PACKED_FIELDS: Set<string>;
export declare const INTENSITY_FIELDS: Set<string>;
/**
 * Mutates output to select optimal color settings given a list of fields
 * @param output - settings object to apply auto selection of colorfield to
 * @param fields - array of string field names. PointField names should already have been checked for support
 * @param { supportsPackedRgbModes, supportsRgbaFieldsMode } - whether or not the message supports packed rgb modes or rgba fields mode
 */
export declare function autoSelectColorSettings<Settings extends ColorModeSettings>(output: Settings, fields: string[], { supportsPackedRgbModes, supportsRgbaFieldsMode, }: {
    supportsPackedRgbModes: boolean;
    supportsRgbaFieldsMode?: boolean;
}): void;
export declare function colorModeSettingsFields<Settings extends ColorModeSettings & BaseSettings>({ msgFields, config, defaults, modifiers: { supportsPackedRgbModes, supportsRgbaFieldsMode, hideFlatColor, hideExplicitAlpha }, }: {
    msgFields?: string[];
    config: Partial<Settings>;
    defaults: Pick<Settings, "gradient">;
    modifiers: {
        supportsPackedRgbModes: boolean;
        supportsRgbaFieldsMode: boolean;
        hideFlatColor?: boolean;
        hideExplicitAlpha?: boolean;
    };
}): NonNullable<SettingsTreeNode["fields"]>;
export declare function colorHasTransparency<Settings extends ColorModeSettings>(settings: Settings): boolean;
export declare const FS_SRGB_TO_LINEAR = "\nvec3 sRGBToLinear(in vec3 value) {\n\treturn vec3(mix(\n    pow(value.rgb * 0.9478672986 + vec3(0.0521327014), vec3(2.4)),\n    value.rgb * 0.0773993808,\n    vec3(lessThanEqual(value.rgb, vec3(0.04045)))\n  ));\n}\n\nvec4 sRGBToLinear(in vec4 value) {\n  return vec4(sRGBToLinear(value.rgb), value.a);\n}\n";
