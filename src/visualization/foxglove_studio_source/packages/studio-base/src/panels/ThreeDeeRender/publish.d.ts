import { MessageDefinition } from "@foxglove/message-definition";
import { Point } from "@foxglove/studio-base/util/geometry";
import { Pose } from "./transforms/geometry";
export declare const PublishRos1Datatypes: Map<string, MessageDefinition>;
export declare const PublishRos2Datatypes: Map<string, MessageDefinition>;
export declare function makePointMessage(point: Point, frameId: string): unknown;
export declare function makePoseMessage(pose: Pose, frameId: string): unknown;
export declare function makePoseEstimateMessage(pose: Pose, frameId: string, xDev: number, yDev: number, thetaDev: number): unknown;
