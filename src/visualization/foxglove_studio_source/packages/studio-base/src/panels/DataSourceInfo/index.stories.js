import { jsx as _jsx } from "react/jsx-runtime";
import { fromDate } from "@foxglove/rostime";
import MockMessagePipelineProvider from "@foxglove/studio-base/components/MessagePipeline/MockMessagePipelineProvider";
import DataSourceInfoPanel from "@foxglove/studio-base/panels/DataSourceInfo";
import { PlayerPresence } from "@foxglove/studio-base/players/types";
import PanelSetup from "@foxglove/studio-base/stories/PanelSetup";
export default {
    title: "panels/DataSourceInfo",
    component: DataSourceInfoPanel,
};
const START_TIME = fromDate(new Date(2022, 1, 22, 1, 11, 11));
const END_TIME = fromDate(new Date(2022, 1, 22, 22, 22, 22));
const TOPICS = [
    { schemaName: "nav_msgs/OccupancyGrid", name: "/map" },
    { schemaName: "visualization_msgs/MarkerArray", name: "/semantic_map" },
    { schemaName: "tf2_msgs/TFMessage", name: "/tf" },
    { schemaName: "nav_msgs/OccupancyGrid", name: "/drivable_area" },
    { schemaName: "sensor_msgs/PointCloud2", name: "/RADAR_FRONT" },
    { schemaName: "sensor_msgs/CompressedImage", name: "/CAM_BACK_RIGHT/image_rect_compressed" },
    { schemaName: "sensor_msgs/CameraInfo", name: "/CAM_BACK_RIGHT/camera_info" },
    { schemaName: "visualization_msgs/ImageMarker", name: "/CAM_BACK/image_markers_lidar" },
    { schemaName: "foxglove_msgs/ImageMarkerArray", name: "/CAM_BACK/image_markers_annotations" },
    { schemaName: "geometry_msgs/PoseStamped", name: "/pose" },
    { schemaName: "sensor_msgs/NavSatFix", name: "/gps" },
    { schemaName: "visualization_msgs/MarkerArray", name: "/markers/annotations" },
    { schemaName: "sensor_msgs/Imu", name: "/imu" },
    { schemaName: "diagnostic_msgs/DiagnosticArray", name: "/diagnostics" },
    { schemaName: "nav_msgs/Odometry", name: "/odom", aliasedFromName: "/old_odom_name" },
];
export const Default = {
    render: () => {
        return (_jsx(MockMessagePipelineProvider, { startTime: START_TIME, endTime: END_TIME, topics: TOPICS, presence: PlayerPresence.PRESENT, children: _jsx(PanelSetup, { fixture: { topics: TOPICS }, children: _jsx(DataSourceInfoPanel, {}) }) }));
    },
};
export const Empty = {
    render: () => {
        return (_jsx(MockMessagePipelineProvider, { noActiveData: true, presence: PlayerPresence.NOT_PRESENT, children: _jsx(PanelSetup, { children: _jsx(DataSourceInfoPanel, {}) }) }));
    },
};
