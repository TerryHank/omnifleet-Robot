import { jsx as _jsx } from "react/jsx-runtime";
import PanelSetup from "@foxglove/studio-base/stories/PanelSetup";
import { QUAT_IDENTITY, rad2deg } from "./common";
import useDelayedFixture from "./useDelayedFixture";
import ThreeDeePanel from "../index";
export default {
    title: "panels/ThreeDeeRender",
    component: ThreeDeePanel,
};
export const GeometryMsgs_Polygon = {
    render: function Story() {
        const topics = [
            { name: "/polygon", schemaName: "geometry_msgs/PolygonStamped" },
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
                    rotation: QUAT_IDENTITY,
                },
            },
            schemaName: "geometry_msgs/TransformStamped",
            sizeInBytes: 0,
        };
        const polygon = {
            topic: "/polygon",
            receiveTime: { sec: 10, nsec: 0 },
            message: {
                header: { seq: 0, stamp: { sec: 0, nsec: 0 }, frame_id: "sensor" },
                polygon: {
                    points: [
                        { x: -1, y: -1, z: 0 },
                        { x: 0, y: 0, z: 2 },
                        { x: 1, y: 1, z: 0 },
                    ],
                },
            },
            schemaName: "geometry_msgs/PolygonStamped",
            sizeInBytes: 0,
        };
        const fixture = useDelayedFixture({
            topics,
            frame: {
                "/polygon": [polygon],
                "/tf": [tf1, tf2],
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
                        distance: 8.25,
                        perspective: true,
                        phi: rad2deg(1),
                        targetOffset: [-0.7, 2.1, 0],
                        thetaOffset: rad2deg(-0.25),
                        fovy: rad2deg(0.75),
                        near: 0.01,
                        far: 5000,
                        target: [0, 0, 0],
                        targetOrientation: [0, 0, 0, 1],
                    },
                    topics: {
                        "/polygon": { visible: true },
                    },
                } }) }));
    },
    parameters: { colorScheme: "dark" },
};
