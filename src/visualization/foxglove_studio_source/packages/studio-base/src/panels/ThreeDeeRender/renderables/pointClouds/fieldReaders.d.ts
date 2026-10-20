import { NumericType, PackedElementField } from "@foxglove/schemas";
import { PointField, PointFieldType } from "../../ros";
export type FieldReader = (view: DataView, pointOffset: number) => number;
export declare function isSupportedField(field: PackedElementField | PointField): boolean;
export declare function getReader(field: PackedElementField | PointField, stride: number, 
/** @see https://www.khronos.org/opengl/wiki/Normalized_Integer */
normalize?: boolean, forceType?: PointFieldType | NumericType): FieldReader | undefined;
