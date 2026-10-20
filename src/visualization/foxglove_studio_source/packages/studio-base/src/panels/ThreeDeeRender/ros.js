// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
export var MarkerType;
(function (MarkerType) {
    MarkerType[MarkerType["ARROW"] = 0] = "ARROW";
    MarkerType[MarkerType["CUBE"] = 1] = "CUBE";
    MarkerType[MarkerType["SPHERE"] = 2] = "SPHERE";
    MarkerType[MarkerType["CYLINDER"] = 3] = "CYLINDER";
    MarkerType[MarkerType["LINE_STRIP"] = 4] = "LINE_STRIP";
    MarkerType[MarkerType["LINE_LIST"] = 5] = "LINE_LIST";
    MarkerType[MarkerType["CUBE_LIST"] = 6] = "CUBE_LIST";
    MarkerType[MarkerType["SPHERE_LIST"] = 7] = "SPHERE_LIST";
    MarkerType[MarkerType["POINTS"] = 8] = "POINTS";
    MarkerType[MarkerType["TEXT_VIEW_FACING"] = 9] = "TEXT_VIEW_FACING";
    MarkerType[MarkerType["MESH_RESOURCE"] = 10] = "MESH_RESOURCE";
    MarkerType[MarkerType["TRIANGLE_LIST"] = 11] = "TRIANGLE_LIST";
})(MarkerType || (MarkerType = {}));
export var MarkerAction;
(function (MarkerAction) {
    MarkerAction[MarkerAction["ADD"] = 0] = "ADD";
    // eslint-disable-next-line @typescript-eslint/no-duplicate-enum-values
    MarkerAction[MarkerAction["MODIFY"] = 0] = "MODIFY";
    MarkerAction[MarkerAction["DELETE"] = 2] = "DELETE";
    MarkerAction[MarkerAction["DELETEALL"] = 3] = "DELETEALL";
})(MarkerAction || (MarkerAction = {}));
export var PointFieldType;
(function (PointFieldType) {
    PointFieldType[PointFieldType["UNKNOWN"] = 0] = "UNKNOWN";
    PointFieldType[PointFieldType["INT8"] = 1] = "INT8";
    PointFieldType[PointFieldType["UINT8"] = 2] = "UINT8";
    PointFieldType[PointFieldType["INT16"] = 3] = "INT16";
    PointFieldType[PointFieldType["UINT16"] = 4] = "UINT16";
    PointFieldType[PointFieldType["INT32"] = 5] = "INT32";
    PointFieldType[PointFieldType["UINT32"] = 6] = "UINT32";
    PointFieldType[PointFieldType["FLOAT32"] = 7] = "FLOAT32";
    PointFieldType[PointFieldType["FLOAT64"] = 8] = "FLOAT64";
})(PointFieldType || (PointFieldType = {}));
export const TIME_ZERO = { sec: 0, nsec: 0 };
export const TRANSFORM_STAMPED_DATATYPES = new Set();
addRosDataType(TRANSFORM_STAMPED_DATATYPES, "geometry_msgs/TransformStamped");
export const TF_DATATYPES = new Set();
addRosDataType(TF_DATATYPES, "tf/tfMessage");
addRosDataType(TF_DATATYPES, "tf2_msgs/TFMessage");
export const MARKER_DATATYPES = new Set();
addRosDataType(MARKER_DATATYPES, "visualization_msgs/Marker");
export const MARKER_ARRAY_DATATYPES = new Set();
addRosDataType(MARKER_ARRAY_DATATYPES, "visualization_msgs/MarkerArray");
// Support the legacy "studio_msgs/MarkerArray" datatype name
addRosDataType(MARKER_ARRAY_DATATYPES, "studio_msgs/MarkerArray");
export const OCCUPANCY_GRID_DATATYPES = new Set();
addRosDataType(OCCUPANCY_GRID_DATATYPES, "nav_msgs/OccupancyGrid");
export const POINTCLOUD_DATATYPES = new Set();
addRosDataType(POINTCLOUD_DATATYPES, "sensor_msgs/PointCloud2");
export const LASERSCAN_DATATYPES = new Set();
addRosDataType(LASERSCAN_DATATYPES, "sensor_msgs/LaserScan");
export const VELODYNE_SCAN_DATATYPES = new Set();
addRosDataType(VELODYNE_SCAN_DATATYPES, "velodyne_msgs/VelodyneScan");
export const POSE_STAMPED_DATATYPES = new Set();
addRosDataType(POSE_STAMPED_DATATYPES, "geometry_msgs/PoseStamped");
export const POSE_WITH_COVARIANCE_STAMPED_DATATYPES = new Set();
addRosDataType(POSE_WITH_COVARIANCE_STAMPED_DATATYPES, "geometry_msgs/PoseWithCovarianceStamped");
export const POSE_ARRAY_DATATYPES = new Set();
addRosDataType(POSE_ARRAY_DATATYPES, "geometry_msgs/PoseArray");
export const NAV_PATH_DATATYPES = new Set();
addRosDataType(NAV_PATH_DATATYPES, "nav_msgs/Path");
export const CAMERA_INFO_DATATYPES = new Set();
addRosDataType(CAMERA_INFO_DATATYPES, "sensor_msgs/CameraInfo");
export const IMAGE_DATATYPES = new Set();
addRosDataType(IMAGE_DATATYPES, "sensor_msgs/Image");
export const COMPRESSED_IMAGE_DATATYPES = new Set();
addRosDataType(COMPRESSED_IMAGE_DATATYPES, "sensor_msgs/CompressedImage");
export const POLYGON_STAMPED_DATATYPES = new Set();
addRosDataType(POLYGON_STAMPED_DATATYPES, "geometry_msgs/PolygonStamped");
export const JOINTSTATE_DATATYPES = new Set();
addRosDataType(JOINTSTATE_DATATYPES, "sensor_msgs/JointState");
export const IMAGE_MARKER_DATATYPES = new Set();
addRosDataType(IMAGE_MARKER_DATATYPES, "visualization_msgs/ImageMarker");
/** Not a real type offered by ROS, but historically Studio has supported it */
export const IMAGE_MARKER_ARRAY_DATATYPES = new Set();
addRosDataType(IMAGE_MARKER_ARRAY_DATATYPES, "visualization_msgs/ImageMarkerArray");
// Expand a single ROS1 dataType into variations for ROS2 and protobufs,
// then add them to the given output set
function addRosDataType(output, dataType) {
    // Add the ROS1 variation: tf2_msgs/TFMessage
    output.add(dataType);
    // Add the ROS2 variation: tf2_msgs/msg/TFMessage
    const parts = dataType.split("/");
    if (parts.length > 1) {
        const base = parts[0];
        const leaf = parts.slice(1).join("/");
        output.add(`${base}/msg/${leaf}`);
    }
    // Add the protobuf variation: ros.tf2_msgs.TFMessage
    output.add("ros." + dataType.split("/").join("."));
    return output;
}
