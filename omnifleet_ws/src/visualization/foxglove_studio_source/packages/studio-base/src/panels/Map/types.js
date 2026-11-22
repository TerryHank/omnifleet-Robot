// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
// https://docs.ros.org/en/api/sensor_msgs/html/msg/NavSatFix.html
export var NavSatFixPositionCovarianceType;
(function (NavSatFixPositionCovarianceType) {
    NavSatFixPositionCovarianceType[NavSatFixPositionCovarianceType["COVARIANCE_TYPE_UNKNOWN"] = 0] = "COVARIANCE_TYPE_UNKNOWN";
    NavSatFixPositionCovarianceType[NavSatFixPositionCovarianceType["COVARIANCE_TYPE_APPROXIMATED"] = 1] = "COVARIANCE_TYPE_APPROXIMATED";
    NavSatFixPositionCovarianceType[NavSatFixPositionCovarianceType["COVARIANCE_TYPE_DIAGONAL_KNOWN"] = 2] = "COVARIANCE_TYPE_DIAGONAL_KNOWN";
    NavSatFixPositionCovarianceType[NavSatFixPositionCovarianceType["COVARIANCE_TYPE_KNOWN"] = 3] = "COVARIANCE_TYPE_KNOWN";
})(NavSatFixPositionCovarianceType || (NavSatFixPositionCovarianceType = {}));
export var NavSatFixStatus;
(function (NavSatFixStatus) {
    NavSatFixStatus[NavSatFixStatus["STATUS_NO_FIX"] = -1] = "STATUS_NO_FIX";
    NavSatFixStatus[NavSatFixStatus["STATUS_FIX"] = 0] = "STATUS_FIX";
    NavSatFixStatus[NavSatFixStatus["STATUS_SBAS_FIX"] = 1] = "STATUS_SBAS_FIX";
    NavSatFixStatus[NavSatFixStatus["STATUS_GBAS_FIX"] = 2] = "STATUS_GBAS_FIX";
})(NavSatFixStatus || (NavSatFixStatus = {}));
// Bits defining which Global Navigation Satellite System signals were
// used by the receiver.
export var NavSatFixService;
(function (NavSatFixService) {
    NavSatFixService[NavSatFixService["SERVICE_GPS"] = 1] = "SERVICE_GPS";
    NavSatFixService[NavSatFixService["SERVICE_GLONASS"] = 2] = "SERVICE_GLONASS";
    NavSatFixService[NavSatFixService["SERVICE_COMPASS"] = 4] = "SERVICE_COMPASS";
    NavSatFixService[NavSatFixService["SERVICE_GALILEO"] = 8] = "SERVICE_GALILEO";
})(NavSatFixService || (NavSatFixService = {}));
