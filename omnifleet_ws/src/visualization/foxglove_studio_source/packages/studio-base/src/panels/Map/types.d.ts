import { MessageEvent } from "@foxglove/studio";
import { FoxgloveMessages } from "@foxglove/studio-base/types/FoxgloveMessages";
export type Point = {
    lat: number;
    lon: number;
};
export type Matrix3x3 = [number, number, number, number, number, number, number, number, number];
export declare enum NavSatFixPositionCovarianceType {
    COVARIANCE_TYPE_UNKNOWN = 0,
    COVARIANCE_TYPE_APPROXIMATED = 1,
    COVARIANCE_TYPE_DIAGONAL_KNOWN = 2,
    COVARIANCE_TYPE_KNOWN = 3
}
export declare enum NavSatFixStatus {
    STATUS_NO_FIX = -1,// unable to fix position
    STATUS_FIX = 0,// unaugmented fix
    STATUS_SBAS_FIX = 1,// with satellite-based augmentation
    STATUS_GBAS_FIX = 2
}
export declare enum NavSatFixService {
    SERVICE_GPS = 1,
    SERVICE_GLONASS = 2,
    SERVICE_COMPASS = 4,// includes BeiDou.
    SERVICE_GALILEO = 8
}
export type NavSatFixMsg = {
    latitude: number;
    longitude: number;
    altitude?: number;
    status?: {
        status: NavSatFixStatus;
        service: NavSatFixService;
    };
    position_covariance?: Matrix3x3;
    position_covariance_type?: NavSatFixPositionCovarianceType;
};
export type MapPanelMessage = MessageEvent<FoxgloveMessages["foxglove.GeoJSON"]> | MessageEvent<NavSatFixMsg>;
