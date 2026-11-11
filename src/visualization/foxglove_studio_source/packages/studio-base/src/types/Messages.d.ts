import { Time } from "@foxglove/rostime";
export type MutablePoint = {
    x: number;
    y: number;
    z: number;
};
export type Point = Readonly<MutablePoint>;
type Points = readonly Point[];
export type MutablePoint2D = {
    x: number;
    y: number;
};
export type Point2D = Readonly<MutablePoint2D>;
export type Header = Readonly<{
    frame_id: string;
    stamp: Time;
    seq: number;
}>;
export type StampedMessage = Readonly<{
    header: Header;
}>;
type Duration = Time;
type MutableOrientation = {
    x: number;
    y: number;
    z: number;
    w: number;
};
export type Scale = Readonly<{
    x: number;
    y: number;
    z: number;
}>;
export type Color = Readonly<{
    r: number;
    g: number;
    b: number;
    a: number;
}>;
export type MutablePose = {
    position: MutablePoint;
    orientation: MutableOrientation;
};
type Colors = readonly Color[];
export type BaseMarker = Readonly<StampedMessage & {
    ns: string;
    id: string | number;
    action: 0 | 1 | 2 | 3;
    pose: MutablePose;
    scale: Scale;
    color?: Color;
    colors?: Colors;
    lifetime?: Time;
    frame_locked: boolean;
    points?: Point[];
    text?: string;
    mesh_resource?: string;
    mesh_use_embedded_materials?: boolean;
    primitive?: string;
    metadata?: Readonly<Record<string, unknown>>;
}>;
type MultiPointMarker = Readonly<{
    points: Points;
    colors?: Colors;
}>;
type ArrowSize = Readonly<{
    shaftLength?: number;
    shaftWidth: number;
    headLength: number;
    headWidth: number;
}>;
export type ArrowMarker = Readonly<BaseMarker & {
    type: 0;
    points?: Points;
    size?: ArrowSize;
}>;
export type CubeMarker = Readonly<BaseMarker & {
    type: 1;
}>;
export type SphereMarker = Readonly<BaseMarker & {
    type: 2;
}>;
export type CylinderMarker = Readonly<BaseMarker & {
    type: 3;
}>;
export type LineStripMarker = Readonly<BaseMarker & MultiPointMarker & {
    closed?: boolean;
    type: 4;
}>;
export type LineListMarker = Readonly<BaseMarker & MultiPointMarker & {
    type: 5;
}>;
export type CubeListMarker = Readonly<BaseMarker & MultiPointMarker & {
    type: 6;
}>;
export type SphereListMarker = Readonly<BaseMarker & MultiPointMarker & {
    type: 7;
}>;
export type PointsMarker = Readonly<BaseMarker & MultiPointMarker & {
    type: 8;
}>;
export type TextMarker = Readonly<BaseMarker & {
    type: 9;
    text: string;
}>;
export type MeshMarker = Readonly<BaseMarker & {
    type: 10;
    mesh_resource: string;
    mesh_use_embedded_materials: boolean;
}>;
export type TriangleListMarker = Readonly<BaseMarker & MultiPointMarker & {
    type: 11;
}>;
export type InstancedLineListMarker = Readonly<BaseMarker & MultiPointMarker & {
    type: 108;
    metadataByIndex?: readonly Readonly<unknown[]>[];
    scaleInvariant?: boolean;
}>;
export type ColorMarker = Readonly<BaseMarker & {
    type: 110;
}>;
export type Marker = ArrowMarker | CubeMarker | CubeListMarker | SphereMarker | SphereListMarker | CylinderMarker | LineStripMarker | LineListMarker | PointsMarker | TextMarker | MeshMarker | TriangleListMarker | InstancedLineListMarker | ColorMarker;
export type MarkerArray = Readonly<{
    markers: readonly Marker[];
}>;
export type PointField = Readonly<{
    name: string;
    offset: number;
    datatype: number;
    count: number;
}>;
export type PointCloud2 = StampedMessage & {
    fields: readonly PointField[];
    height: number;
    width: number;
    is_bigendian: boolean;
    point_step: number;
    row_step: number;
    data: Uint8Array;
    is_dense: boolean | number;
    type: 102;
    pose?: MutablePose;
};
export type VelodynePacket = Readonly<{
    stamp: Time;
    data: Uint8Array;
}>;
export type VelodyneScan = Readonly<StampedMessage & {
    packets: VelodynePacket[];
}>;
export declare enum ImageMarkerType {
    CIRCLE = 0,
    LINE_STRIP = 1,
    LINE_LIST = 2,
    POLYGON = 3,
    POINTS = 4,
    TEXT = 5
}
export declare enum ImageMarkerAction {
    ADD = 0,
    REMOVE = 1
}
export type ImageMarker = Readonly<{
    header: Header;
    ns: string;
    id: number;
    type: ImageMarkerType;
    action: ImageMarkerAction;
    position: Point;
    scale: number;
    outline_color: Color;
    filled: boolean;
    fill_color: Color;
    lifetime: Duration;
    points: Points;
    outline_colors: Colors;
    text?: {
        data: string;
    };
}>;
export type ImageMarkerArray = Readonly<{
    markers: ImageMarker[];
}>;
export {};
