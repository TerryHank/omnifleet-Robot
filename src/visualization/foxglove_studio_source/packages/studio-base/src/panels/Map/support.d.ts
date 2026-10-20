import { GeoJsonObject } from "geojson";
import { PathOptions } from "leaflet";
import { MessageEvent } from "@foxglove/studio";
import { FoxgloveMessages } from "@foxglove/studio-base/types/FoxgloveMessages";
import { MapPanelMessage, NavSatFixMsg } from "./types";
export type GeoJsonMessage = MessageEvent<FoxgloveMessages["foxglove.GeoJSON"]>;
/**
 * @returns true if the message event status indicates there is a fix
 */
export declare function hasFix(ev: MessageEvent<NavSatFixMsg>): boolean;
export declare function isGeoJSONMessage(msgEvent: MessageEvent): msgEvent is GeoJsonMessage;
/**
 * Verify that the message is either a GeoJSON message or a NavSatFix message with
 * finite latitude and longitude so we can actually display it.
 */
export declare function isValidMapMessage(msgEvent: MessageEvent): msgEvent is MapPanelMessage;
export declare function isSupportedSchema(schemaName: string): boolean;
/**
 * Parse a geoJSON string into individual GeoJsonObjects, extracting the nonstandard
 * `style` property, if it exists.
 */
export declare function parseGeoJSON(json: string): Array<{
    object: GeoJsonObject;
    style: PathOptions;
}>;
