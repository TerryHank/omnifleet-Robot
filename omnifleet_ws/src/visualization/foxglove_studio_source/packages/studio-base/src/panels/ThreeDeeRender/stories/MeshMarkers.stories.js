import { jsx as _jsx } from "react/jsx-runtime";
import PanelSetup from "@foxglove/studio-base/stories/PanelSetup";
import { makeColor, OBJ_CUBE_MESH_RESOURCE, QUAT_IDENTITY, STL_CUBE_MESH_RESOURCE } from "./common";
import useDelayedFixture from "./useDelayedFixture";
import { DEFAULT_CAMERA_STATE } from "../camera";
import ThreeDeePanel from "../index";
export default {
    title: "panels/ThreeDeeRender",
    component: ThreeDeePanel,
};
export const MeshMarkers = {
    render: function Story() {
        const topics = [
            { name: "/markersOutline", schemaName: "visualization_msgs/Marker" },
            { name: "/markersNoOutline", schemaName: "visualization_msgs/Marker" },
            { name: "/tf", schemaName: "geometry_msgs/TransformStamped" },
        ];
        function getMeshesInFrame(topic, frame_id) {
            const stlMesh = {
                topic,
                receiveTime: { sec: 10, nsec: 0 },
                message: {
                    header: { seq: 0, stamp: { sec: 0, nsec: 0 }, frame_id },
                    id: 0,
                    ns: "stl",
                    type: 10,
                    action: 0,
                    frame_locked: false,
                    pose: {
                        position: { x: 0, y: -1, z: 0 },
                        orientation: { x: 0, y: 0, z: 0, w: 1 },
                    },
                    scale: { x: 0.5, y: 0.5, z: 0.5 },
                    color: makeColor("#8bc34a", 0.5),
                    points: [],
                    colors: [],
                    text: "",
                    mesh_resource: STL_CUBE_MESH_RESOURCE,
                    mesh_use_embedded_materials: true,
                    lifetime: { sec: 0, nsec: 0 },
                },
                schemaName: "visualization_msgs/Marker",
                sizeInBytes: 0,
            };
            const stlColoredMesh = {
                ...stlMesh,
                message: {
                    ...stlMesh.message,
                    id: 1,
                    mesh_use_embedded_materials: false,
                    pose: { position: { x: -1, y: 0, z: 0 }, orientation: stlMesh.message.pose.orientation },
                },
            };
            const objMesh = {
                topic,
                receiveTime: { sec: 10, nsec: 0 },
                message: {
                    header: { seq: 0, stamp: { sec: 0, nsec: 0 }, frame_id },
                    id: 0,
                    ns: "obj",
                    type: 10,
                    action: 0,
                    frame_locked: false,
                    pose: {
                        position: { x: 1, y: 0, z: 0 },
                        orientation: { x: 0, y: 0, z: 0, w: 1 },
                    },
                    scale: { x: 0.25, y: 0.25, z: 0.25 },
                    color: makeColor("#ff0000"),
                    points: [],
                    colors: [],
                    text: "",
                    mesh_resource: OBJ_CUBE_MESH_RESOURCE,
                    mesh_use_embedded_materials: true,
                    lifetime: { sec: 0, nsec: 0 },
                },
                schemaName: "visualization_msgs/Marker",
                sizeInBytes: 0,
            };
            return [stlMesh, stlColoredMesh, objMesh];
        }
        const outlineMeshes = getMeshesInFrame("/markersOutline", "outline");
        const noOutlineMeshes = getMeshesInFrame("/markersNoOutline", "no-outline");
        const tf1 = {
            topic: "/tf",
            receiveTime: { sec: 10, nsec: 0 },
            message: {
                header: { seq: 0, stamp: { sec: 0, nsec: 0 }, frame_id: "" },
                child_frame_id: "outline",
                transform: {
                    translation: { x: 0, y: -1, z: 0 },
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
                header: { seq: 0, stamp: { sec: 0, nsec: 0 }, frame_id: "" },
                child_frame_id: "no-outline",
                transform: {
                    translation: { x: 0, y: 1, z: 0 },
                    rotation: QUAT_IDENTITY,
                },
            },
            schemaName: "geometry_msgs/TransformStamped",
            sizeInBytes: 0,
        };
        const fixture = useDelayedFixture({
            topics,
            frame: {
                "/markersOutline": outlineMeshes,
                "/markersNoOutline": noOutlineMeshes,
                "/tf": [tf1, tf2],
            },
            capabilities: [],
            activeData: {
                currentTime: { sec: 0, nsec: 0 },
            },
        });
        return (_jsx(PanelSetup, { fixture: fixture, children: _jsx(ThreeDeePanel, { overrideConfig: {
                    ...ThreeDeePanel.defaultConfig,
                    layers: {
                        grid: { layerId: "foxglove.Grid" },
                    },
                    cameraState: { ...DEFAULT_CAMERA_STATE, distance: 5, thetaOffset: 50 },
                    topics: {
                        "/markersOutline": { visible: true },
                        "/markersNoOutline": { visible: true, showOutlines: false },
                    },
                } }) }));
    },
    parameters: { colorScheme: "dark" },
};
