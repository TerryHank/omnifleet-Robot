import { jsx as _jsx } from "react/jsx-runtime";
import PanelSetup from "@foxglove/studio-base/stories/PanelSetup";
import { makeColor, QUAT_IDENTITY, rad2deg, SENSOR_FRAME_ID } from "./common";
import useDelayedFixture from "./useDelayedFixture";
import ThreeDeePanel from "../index";
import { MarkerType } from "../ros";
export default {
    title: "panels/ThreeDeeRender",
    component: ThreeDeePanel,
};
export const LabelMarkers = {
    render: function Story() {
        const topics = [
            { name: "/tf", schemaName: "geometry_msgs/TransformStamped" },
            { name: "/labels", schemaName: "visualization_msgs/Marker" },
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
                child_frame_id: SENSOR_FRAME_ID,
                transform: {
                    translation: { x: 0, y: 1, z: 0 },
                    rotation: QUAT_IDENTITY,
                },
            },
            schemaName: "geometry_msgs/TransformStamped",
            sizeInBytes: 0,
        };
        let id = 0;
        const makeLabel = (text, position, colorHex, alpha = 1) => {
            return {
                topic: "/labels",
                receiveTime: { sec: 10, nsec: 0 },
                message: {
                    header: { seq: 0, stamp: { sec: 0, nsec: 0 }, frame_id: SENSOR_FRAME_ID },
                    id: id++,
                    ns: "",
                    action: 0,
                    type: MarkerType.TEXT_VIEW_FACING,
                    text,
                    frame_locked: true,
                    color: makeColor(colorHex, alpha),
                    pose: { position, orientation: QUAT_IDENTITY },
                    scale: { x: 0, y: 0, z: 0.1 },
                },
                schemaName: "visualization_msgs/Marker",
                sizeInBytes: 0,
            };
        };
        const label1 = makeLabel("Hello, world!", { x: -2, y: 1, z: 0 }, "#e60049");
        const label2 = makeLabel("Hello, world!", { x: -1, y: 1, z: 0 }, "#0bb4ff");
        const label3 = makeLabel("Hello, world!", { x: 0, y: 1, z: 0 }, "#50e991");
        const label4 = makeLabel("Hello, world!", { x: 1, y: 1, z: 0 }, "#e6d800");
        const label5 = makeLabel("Hello, world!", { x: -2, y: 0, z: 0 }, "#9b19f5");
        const label6 = makeLabel("Hello, world!", { x: -1, y: 0, z: 0 }, "#ffa300");
        const label7 = makeLabel("Hello, world!", { x: 1, y: 0, z: 0 }, "#dc0ab4");
        const label8 = makeLabel("Hello, world!", { x: -2, y: -1, z: 0 }, "#b3d4ff");
        const label9 = makeLabel("Hello, world!", { x: -1, y: -1, z: 0 }, "#00bfa0");
        const label10 = makeLabel("Hello, world!", { x: 0, y: -1, z: 0 }, "#b30000");
        const label11 = makeLabel("Hello, world!", { x: 1, y: -1, z: 0 }, "#7c1158");
        const fixture = useDelayedFixture({
            topics,
            frame: {
                "/tf": [tf1, tf2],
                // prettier-ignore
                "/labels": [label1, label2, label3, label4, label5, label6, label7, label8, label9, label10, label11],
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
                        distance: 5.5,
                        perspective: true,
                        phi: rad2deg(0.5),
                        targetOffset: [-0.5, 0.75, 0],
                        thetaOffset: rad2deg(-0.25),
                        fovy: rad2deg(0.75),
                        near: 0.01,
                        far: 5000,
                        target: [0, 0, 0],
                        targetOrientation: [0, 0, 0, 1],
                    },
                    layers: {
                        grid: { layerId: "foxglove.Grid" },
                    },
                    topics: {
                        "/labels": { visible: true },
                    },
                } }) }));
    },
};
