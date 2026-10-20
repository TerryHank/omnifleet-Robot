import { jsx as _jsx } from "react/jsx-runtime";
import { fromSec } from "@foxglove/rostime";
import PanelSetup from "@foxglove/studio-base/stories/PanelSetup";
import { makePass, QUAT_IDENTITY, rad2deg, TEST_COLORS } from "./common";
import useDelayedFixture from "./useDelayedFixture";
import ThreeDeePanel from "../index";
export default {
    title: "panels/ThreeDeeRender",
    component: ThreeDeePanel,
};
export const LargeTransform = {
    render: function Story() {
        const topics = [
            { name: "/markers", schemaName: "visualization_msgs/Marker" },
            { name: "/tf", schemaName: "geometry_msgs/TransformStamped" },
        ];
        const tf1 = {
            topic: "/tf",
            receiveTime: { sec: 10, nsec: 0 },
            message: {
                header: { seq: 0, stamp: { sec: 0, nsec: 0 }, frame_id: "map" },
                child_frame_id: "odom",
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
                header: { seq: 0, stamp: { sec: 0, nsec: 0 }, frame_id: "odom" },
                child_frame_id: "base_link",
                transform: {
                    translation: { x: 1, y: 0, z: 0 },
                    rotation: QUAT_IDENTITY,
                },
            },
            schemaName: "geometry_msgs/TransformStamped",
            sizeInBytes: 0,
        };
        const pass1 = makePass({
            id: 1,
            frame_id: "map",
            stamp: fromSec(0),
            colorHex: TEST_COLORS.MARKER_GREEN1,
            pose: { position: { x: 1e7, y: 0, z: 0 }, orientation: QUAT_IDENTITY },
        });
        const pass2 = makePass({
            id: 2,
            frame_id: "base_link",
            stamp: fromSec(0),
            colorHex: TEST_COLORS.MARKER_GREEN2,
        });
        const pass3 = makePass({
            id: 3,
            frame_id: "odom",
            stamp: fromSec(0),
            colorHex: TEST_COLORS.MARKER_GREEN3,
            pose: { position: { x: 2, y: 0, z: 0 }, orientation: QUAT_IDENTITY },
        });
        const fixture = useDelayedFixture({
            topics,
            frame: {
                "/markers": [pass1, pass2, pass3],
                "/tf": [tf1, tf2],
            },
            capabilities: [],
            activeData: {
                currentTime: { sec: 0, nsec: 0 },
            },
        });
        return (_jsx(PanelSetup, { fixture: fixture, children: _jsx(ThreeDeePanel, { overrideConfig: {
                    followTf: "base_link",
                    layers: {
                        grid: {
                            layerId: "foxglove.Grid",
                            position: [0, 0, -0.25],
                        },
                    },
                    cameraState: {
                        distance: 3,
                        perspective: true,
                        phi: rad2deg(1),
                        targetOffset: [0, 0, 0],
                        thetaOffset: rad2deg(0),
                        fovy: rad2deg(0.75),
                        near: 0.01,
                        far: 5000,
                        target: [0, 0, 0],
                        targetOrientation: [0, 0, 0, 1],
                    },
                    topics: {
                        "/markers": { visible: true },
                    },
                } }) }));
    },
    parameters: { colorScheme: "dark" },
};
