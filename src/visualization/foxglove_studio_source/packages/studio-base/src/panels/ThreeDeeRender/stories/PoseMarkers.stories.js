import { jsx as _jsx } from "react/jsx-runtime";
import PanelSetup from "@foxglove/studio-base/stories/PanelSetup";
import { BASE_LINK_FRAME_ID, FIXED_FRAME_ID, QUAT_IDENTITY, rad2deg, SENSOR_FRAME_ID, } from "./common";
import useDelayedFixture from "./useDelayedFixture";
import ThreeDeePanel from "../index";
export default {
    title: "panels/ThreeDeeRender",
    component: ThreeDeePanel,
};
export const PoseMarkers = {
    render: function Story() {
        const topics = [
            { name: "/tf", schemaName: "geometry_msgs/TransformStamped" },
            { name: "/pose", schemaName: "geometry_msgs/PoseStamped" },
            { name: "/pose_with_covariance", schemaName: "geometry_msgs/PoseWithCovarianceStamped" },
            {
                name: "/pose_with_hidden_covariance",
                schemaName: "geometry_msgs/PoseWithCovarianceStamped",
            },
            { name: "/pose_axis_with_covariance", schemaName: "geometry_msgs/PoseWithCovarianceStamped" },
        ];
        const tf1 = {
            topic: "/tf",
            receiveTime: { sec: 10, nsec: 0 },
            message: {
                header: { seq: 0, stamp: { sec: 0, nsec: 0 }, frame_id: FIXED_FRAME_ID },
                child_frame_id: BASE_LINK_FRAME_ID,
                transform: {
                    translation: { x: 1e7, y: 0, z: 0 },
                    rotation: QUAT_IDENTITY,
                },
            },
            schemaName: "geometry_msgs/TransformStamped",
            sizeInBytes: 0,
        };
        const tf2 = {
            topic: "/tf",
            receiveTime: { sec: 10, nsec: 0 },
            message: {
                header: { seq: 0, stamp: { sec: 0, nsec: 0 }, frame_id: BASE_LINK_FRAME_ID },
                child_frame_id: SENSOR_FRAME_ID,
                transform: {
                    translation: { x: 0, y: 0, z: 1 },
                    rotation: { x: 0.383, y: 0, z: 0, w: 0.924 },
                },
            },
            schemaName: "geometry_msgs/TransformStamped",
            sizeInBytes: 0,
        };
        const pose1 = {
            topic: "/pose",
            receiveTime: { sec: 10, nsec: 0 },
            message: {
                header: { seq: 0, stamp: { sec: 0, nsec: 0 }, frame_id: SENSOR_FRAME_ID },
                pose: {
                    position: { x: 0, y: 0, z: -1 },
                    orientation: { x: 0, y: -Math.SQRT1_2, z: 0, w: Math.SQRT1_2 },
                },
            },
            schemaName: "geometry_msgs/PoseStamped",
            sizeInBytes: 0,
        };
        const pose2 = {
            topic: "/pose_with_covariance",
            receiveTime: { sec: 10, nsec: 0 },
            message: {
                header: { seq: 0, stamp: { sec: 0, nsec: 0 }, frame_id: BASE_LINK_FRAME_ID },
                pose: {
                    pose: {
                        position: { x: 0, y: 0, z: 0 },
                        orientation: QUAT_IDENTITY,
                    },
                    // prettier-ignore
                    covariance: [
                        2 * 2, 0, 0, 0, 0, 0,
                        0, 0.15 * 0.15, 0, 0, 0, 0,
                        0, 0, 0.3 * 0.3, 0, 0, 0,
                        0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0,
                    ],
                },
            },
            schemaName: "geometry_msgs/PoseWithCovarianceStamped",
            sizeInBytes: 0,
        };
        const pose3 = {
            topic: "/pose_with_hidden_covariance",
            receiveTime: { sec: 10, nsec: 0 },
            message: {
                header: { seq: 0, stamp: { sec: 0, nsec: 0 }, frame_id: SENSOR_FRAME_ID },
                pose: {
                    pose: {
                        position: { x: -1, y: 0, z: -1 },
                        orientation: { x: 0, y: -Math.SQRT1_2, z: 0, w: Math.SQRT1_2 },
                    },
                    // prettier-ignore
                    covariance: [
                        1, 0, 0, 0, 0, 0,
                        0, 1, 0, 0, 0, 0,
                        0, 0, 1, 0, 0, 0,
                        0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0,
                    ],
                },
            },
            schemaName: "geometry_msgs/PoseWithCovarianceStamped",
            sizeInBytes: 0,
        };
        const pose4 = {
            topic: "/pose_axis_with_covariance",
            receiveTime: { sec: 10, nsec: 0 },
            message: {
                header: { seq: 0, stamp: { sec: 0, nsec: 0 }, frame_id: SENSOR_FRAME_ID },
                pose: {
                    pose: {
                        position: { x: 1, y: 0, z: -1 },
                        orientation: { x: 0, y: -Math.SQRT1_2, z: 0, w: Math.SQRT1_2 },
                    },
                    // prettier-ignore
                    covariance: [
                        1, 0, 0, 0, 0, 0,
                        0, 1, 0, 0, 0, 0,
                        0, 0, 1, 0, 0, 0,
                        0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0,
                    ],
                },
            },
            schemaName: "geometry_msgs/PoseWithCovarianceStamped",
            sizeInBytes: 0,
        };
        const fixture = useDelayedFixture({
            topics,
            frame: {
                "/tf": [tf1, tf2],
                "/pose": [pose1],
                "/pose_with_covariance": [pose2],
                "/pose_with_hidden_covariance": [pose3],
                "/pose_axis_with_covariance": [pose4],
            },
            capabilities: [],
            activeData: {
                currentTime: { sec: 0, nsec: 0 },
            },
        });
        return (_jsx(PanelSetup, { fixture: fixture, children: _jsx(ThreeDeePanel, { overrideConfig: {
                    ...ThreeDeePanel.defaultConfig,
                    followTf: "base_link",
                    cameraState: {
                        distance: 4,
                        perspective: true,
                        phi: rad2deg(1),
                        targetOffset: [-0.6, 0.5, 0],
                        thetaOffset: rad2deg(-1),
                        fovy: rad2deg(0.75),
                        near: 0.01,
                        far: 5000,
                        target: [0, 0, 0],
                        targetOrientation: [0, 0, 0, 1],
                    },
                    topics: {
                        "/pose": {
                            visible: true,
                            type: "arrow",
                            color: "rgba(107, 220, 255, 0.5)",
                        },
                        "/pose_with_covariance": {
                            visible: true,
                            type: "arrow",
                        },
                        "/pose_with_hidden_covariance": {
                            visible: true,
                            type: "arrow",
                            showCovariance: false,
                            covarianceColor: "rgba(255, 0, 0, 1)",
                        },
                        "/pose_axis_with_covariance": {
                            visible: true,
                        },
                    },
                } }) }));
    },
    parameters: { colorScheme: "dark" },
};
