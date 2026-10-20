import { NavSatFixMsg } from "@foxglove/studio-base/panels/Map/types";
/**
 * Calculates the accuracy of a NavSatFix message, based on its type, and returns
 * information suitable for display as a leaflet Ellipse.
 *
 * @param msg NavSatFix
 * @returns radii and tilt (degrees from W)
 */
export declare function getAccuracy(msg: NavSatFixMsg): {
    radii: [number, number];
    tilt: number;
} | undefined;
