import { jsx as _jsx } from "react/jsx-runtime";
import { quat } from "gl-matrix";
import PanelSetup from "@foxglove/studio-base/stories/PanelSetup";
import { QUAT_IDENTITY, rad2deg } from "./common";
import useDelayedFixture from "./useDelayedFixture";
import ThreeDeePanel from "../index";
export default {
    title: "panels/ThreeDeeRender",
    component: ThreeDeePanel,
};
const vec4ToOrientation = ([x, y, z, w]) => ({ x, y, z, w });
export const GeometryMsgs_PoseStamped = {
    render: function Story() {
        const topics = [
            { name: "/tf", schemaName: "geometry_msgs/TransformStamped" },
            { name: "/pose1", schemaName: "geometry_msgs/PoseStamped" },
            { name: "/pose2", schemaName: "geometry_msgs/PoseStamped" },
            { name: "/pose3", schemaName: "geometry_msgs/PoseStamped" },
        ];
        const tf1 = {
            topic: "/tf",
            receiveTime: { sec: 10, nsec: 0 },
            message: {
                header: { seq: 0, stamp: { sec: 0, nsec: 0 }, frame_id: "map" },
                child_frame_id: "base_link",
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
                header: { seq: 0, stamp: { sec: 0, nsec: 0 }, frame_id: "base_link" },
                child_frame_id: "sensor",
                transform: {
                    translation: { x: 0, y: -5, z: 0 },
                    rotation: QUAT_IDENTITY,
                },
            },
            schemaName: "geometry_msgs/TransformStamped",
            sizeInBytes: 0,
        };
        const pose1 = {
            topic: "/pose1",
            receiveTime: { sec: 10, nsec: 0 },
            message: {
                header: { seq: 0, stamp: { sec: 0, nsec: 0 }, frame_id: "base_link" },
                pose: {
                    position: { x: 2, y: 0, z: 0 },
                    orientation: QUAT_IDENTITY,
                },
            },
            schemaName: "geometry_msgs/PoseStamped",
            sizeInBytes: 0,
        };
        const pose2 = {
            topic: "/pose2",
            receiveTime: { sec: 10, nsec: 0 },
            message: {
                header: { seq: 0, stamp: { sec: 0, nsec: 0 }, frame_id: "sensor" },
                pose: {
                    position: { x: 0, y: 3, z: 0 },
                    orientation: vec4ToOrientation(quat.rotateZ(quat.create(), quat.create(), Math.PI / 2)),
                },
            },
            schemaName: "geometry_msgs/PoseStamped",
            sizeInBytes: 0,
        };
        const pose3 = {
            topic: "/pose3",
            receiveTime: { sec: 10, nsec: 0 },
            message: {
                header: { seq: 0, stamp: { sec: 0, nsec: 0 }, frame_id: "base_link" },
                pose: {
                    position: { x: 0, y: 2, z: 0 },
                    orientation: vec4ToOrientation(quat.rotateZ(quat.create(), quat.create(), Math.PI / 4)),
                },
            },
            schemaName: "geometry_msgs/PoseStamped",
            sizeInBytes: 0,
        };
        const fixture = useDelayedFixture({
            topics,
            frame: {
                "/tf": [tf1, tf2],
                "/pose1": [pose1],
                "/pose2": [pose2],
                "/pose3": [pose3],
            },
            capabilities: [],
            activeData: {
                currentTime: { sec: 0, nsec: 0 },
            },
        });
        return (_jsx(PanelSetup, { fixture: fixture, children: _jsx(ThreeDeePanel, { overrideConfig: {
                    followTf: "base_link",
                    topics: {
                        "/pose1": {
                            visible: true,
                            type: "arrow",
                        },
                        "/pose2": {
                            visible: true,
                            type: "arrow",
                            arrowScale: [2, 1, 1],
                            color: "rgba(0, 255, 0, 0.3)",
                        },
                        "/pose3": {
                            visible: true,
                            axisScale: Math.sqrt(8),
                        },
                    },
                    layers: {
                        grid: { layerId: "foxglove.Grid" },
                    },
                    cameraState: {
                        distance: 15,
                        perspective: false,
                        phi: rad2deg(0),
                        targetOffset: [-0.6, 0.5, 0],
                        thetaOffset: rad2deg(0),
                        fovy: rad2deg(0.75),
                        near: 0.01,
                        far: 5000,
                        target: [0, 0, 0],
                        targetOrientation: [0, 0, 0, 1],
                    },
                } }) }));
    },
    parameters: { colorScheme: "dark" },
};
