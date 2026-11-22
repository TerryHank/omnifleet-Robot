// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { NavSatFixStatus } from "./types";
/**
 * @returns true if the message event status indicates there is a fix
 */
export function hasFix(ev) {
    switch (ev.message.status?.status) {
        case NavSatFixStatus.STATUS_GBAS_FIX:
        case NavSatFixStatus.STATUS_SBAS_FIX:
        case NavSatFixStatus.STATUS_FIX:
            return true;
        case NavSatFixStatus.STATUS_NO_FIX:
        case undefined:
        default:
            return false;
    }
}
export function isGeoJSONMessage(msgEvent) {
    const datatype = msgEvent.schemaName;
    return (datatype === "foxglove_msgs/GeoJSON" ||
        datatype === "foxglove_msgs/msg/GeoJSON" ||
        datatype === "foxglove::GeoJSON" ||
        datatype === "foxglove.GeoJSON");
}
/**
 * Verify that the message is either a GeoJSON message or a NavSatFix message with
 * finite latitude and longitude so we can actually display it.
 */
export function isValidMapMessage(msgEvent) {
    if (isGeoJSONMessage(msgEvent)) {
        return true;
    }
    const message = msgEvent.message;
    return (message.latitude != undefined &&
        isFinite(message.latitude) &&
        message.longitude != undefined &&
        isFinite(message.longitude));
}
export function isSupportedSchema(schemaName) {
    switch (schemaName) {
        case "sensor_msgs/NavSatFix":
        case "sensor_msgs/msg/NavSatFix":
        case "ros.sensor_msgs.NavSatFix":
        case "foxglove_msgs/LocationFix":
        case "foxglove_msgs/msg/LocationFix":
        case "foxglove.LocationFix":
        case "foxglove::LocationFix":
        case "foxglove_msgs/GeoJSON":
        case "foxglove_msgs/msg/GeoJSON":
        case "foxglove::GeoJSON":
        case "foxglove.GeoJSON":
            return true;
        default:
            return false;
    }
}
/**
 * Parse a geoJSON string into individual GeoJsonObjects, extracting the nonstandard
 * `style` property, if it exists.
 */
export function parseGeoJSON(json) {
    try {
        const parsed = JSON.parse(json);
        const geoJsons = parsed ? (Array.isArray(parsed) ? parsed : [parsed]) : [];
        return geoJsons.flatMap((geoJson) => {
            switch (geoJson.type) {
                case "Feature": {
                    const style = geoJson.properties?.style ?? {};
                    return { object: geoJson, style };
                }
                case "FeatureCollection":
                    return (geoJson.features ?? []).map((feature) => {
                        const style = feature.properties?.style ?? {};
                        return { object: feature, style };
                    });
                default:
                    return { object: geoJson, style: {} };
            }
        });
    }
    catch (error) {
        console.error(error);
        return [];
    }
}
