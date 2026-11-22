import { ros1, ros2galactic } from "@foxglove/rosmsg-msgs-common";
import { fromDate } from "@foxglove/rostime";
import { makeCovarianceArray } from "@foxglove/studio-base/util/geometry";
export const PublishRos1Datatypes = new Map([
    "geometry_msgs/Point",
    "geometry_msgs/PointStamped",
    "geometry_msgs/Pose",
    "geometry_msgs/PoseStamped",
    "geometry_msgs/PoseWithCovariance",
    "geometry_msgs/PoseWithCovarianceStamped",
    "geometry_msgs/Quaternion",
    "std_msgs/Header",
].map((type) => [type, ros1[type]]));
export const PublishRos2Datatypes = new Map([
    "geometry_msgs/Point",
    "geometry_msgs/PointStamped",
    "geometry_msgs/Pose",
    "geometry_msgs/PoseStamped",
    "geometry_msgs/PoseWithCovariance",
    "geometry_msgs/PoseWithCovarianceStamped",
    "geometry_msgs/Quaternion",
    "std_msgs/Header",
].map((type) => [type, ros2galactic[type]]));
export function makePointMessage(point, frameId) {
    const time = fromDate(new Date());
    return {
        // seq is omitted since it is not present in ros2
        header: { stamp: time, frame_id: frameId },
        point: { x: point.x, y: point.y, z: 0 },
    };
}
export function makePoseMessage(pose, frameId) {
    const time = fromDate(new Date());
    return {
        // seq is omitted since it is not present in ros2
        header: { stamp: time, frame_id: frameId },
        pose,
    };
}
export function makePoseEstimateMessage(pose, frameId, xDev, yDev, thetaDev) {
    const time = fromDate(new Date());
    return {
        // seq is omitted since it is not present in ros2
        header: { stamp: time, frame_id: frameId },
        pose: {
            covariance: makeCovarianceArray(xDev, yDev, thetaDev),
            pose,
        },
    };
}
