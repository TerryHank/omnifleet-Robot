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
export const GeometryMsgs_PoseArray = {
    render: function Story() {
        const topics = [
            { name: "/baselink_path", schemaName: "geometry_msgs/PoseArray" },
            { name: "/sensor_path", schemaName: "geometry_msgs/PoseArray" },
            { name: "/sensor_path2", schemaName: "geometry_msgs/PoseArray" },
            { name: "/tf", schemaName: "geometry_msgs/TransformStamped" },
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
                    translation: { x: 0, y: 0, z: 1 },
                    rotation: vec4ToOrientation(quat.rotateZ(quat.create(), quat.create(), Math.PI / 2)),
                },
            },
            schemaName: "geometry_msgs/TransformStamped",
            sizeInBytes: 0,
        };
        const tf3 = {
            topic: "/tf",
            receiveTime: { sec: 10, nsec: 0 },
            message: {
                header: { seq: 0, stamp: { sec: 10, nsec: 0 }, frame_id: "base_link" },
                child_frame_id: "sensor",
                transform: {
                    translation: { x: 0, y: 5, z: 1 },
                    rotation: QUAT_IDENTITY,
                },
            },
            schemaName: "geometry_msgs/TransformStamped",
            sizeInBytes: 0,
        };
        const q = () => [0, 0, 0, 1];
        const identity = q();
        const makeOrientation = (i) => {
            const o = quat.rotateZ(q(), identity, (Math.PI / 2) * (i / 9));
            return { x: o[0], y: o[1], z: o[2], w: o[3] };
        };
        const baseLinkPath = {
            topic: "/baselink_path",
            receiveTime: { sec: 3, nsec: 0 },
            message: {
                header: { seq: 0, stamp: { sec: 0, nsec: 0 }, frame_id: "base_link" },
                poses: [...Array(10)].map((_, i) => ({
                    position: { x: 3, y: i / 4, z: 1 },
                    orientation: makeOrientation(i),
                })),
            },
            schemaName: "geometry_msgs/PoseArray",
            sizeInBytes: 0,
        };
        const sensorPath = {
            topic: "/sensor_path",
            receiveTime: { sec: 3, nsec: 0 },
            message: {
                header: { seq: 0, stamp: { sec: 0, nsec: 0 }, frame_id: "sensor" },
                poses: [...Array(10)].map((_, i) => ({
                    position: { x: 2, y: i / 4, z: 0 },
                    orientation: makeOrientation(i),
                })),
            },
            schemaName: "geometry_msgs/PoseArray",
            sizeInBytes: 0,
        };
        const sensorPath2 = {
            topic: "/sensor_path2",
            receiveTime: { sec: 3, nsec: 0 },
            message: {
                header: { seq: 0, stamp: { sec: 0, nsec: 0 }, frame_id: "sensor" },
                poses: [...Array(10)].map((_, i) => ({
                    position: { x: -i / 4, y: 2, z: 0 },
                    orientation: makeOrientation(i),
                })),
            },
            schemaName: "geometry_msgs/PoseArray",
            sizeInBytes: 0,
        };
        const fixture = useDelayedFixture({
            topics,
            frame: {
                "/baselink_path": [baseLinkPath],
                "/sensor_path": [sensorPath],
                "/sensor_path2": [sensorPath2],
                "/tf": [tf1, tf2, tf3],
            },
            capabilities: [],
            activeData: {
                currentTime: { sec: 3, nsec: 0 },
            },
        });
        return (_jsx(PanelSetup, { fixture: fixture, children: _jsx(ThreeDeePanel, { overrideConfig: {
                    followTf: "base_link",
                    topics: {
                        "/sensor_path": {
                            visible: true,
                            type: "arrow",
                            gradient: ["rgba(0, 255, 0, 0.2)", "rgba(0, 255, 127, 1.0)"],
                            arrowScale: [1, 0.5, 0.01],
                        },
                        "/sensor_path2": {
                            visible: true,
                            axisScale: 0.5,
                        },
                        "/baselink_path": {
                            visible: true,
                            type: "arrow",
                        },
                    },
                    cameraState: {
                        distance: 15,
                        perspective: true,
                        phi: rad2deg(0.25),
                        targetOffset: [0, 2, 0],
                        thetaOffset: rad2deg(-0.25),
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
