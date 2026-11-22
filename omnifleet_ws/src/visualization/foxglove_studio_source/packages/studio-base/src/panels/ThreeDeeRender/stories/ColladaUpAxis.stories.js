import { jsx as _jsx } from "react/jsx-runtime";
import PanelSetup from "@foxglove/studio-base/stories/PanelSetup";
import { COLLADA_CONE_Y_UP_MESH_RESOURCE, COLLADA_CONE_Z_UP_MESH_RESOURCE } from "./common";
import useDelayedFixture from "./useDelayedFixture";
import { DEFAULT_CAMERA_STATE } from "../camera";
import ThreeDeePanel from "../index";
export default {
    title: "panels/ThreeDeeRender",
    component: ThreeDeePanel,
};
const baseMeshMarker = {
    topic: "/markers",
    receiveTime: { sec: 10, nsec: 0 },
    message: {
        header: { seq: 0, stamp: { sec: 0, nsec: 0 }, frame_id: "" },
        id: 0,
        ns: "",
        type: 10,
        action: 0,
        frame_locked: false,
        pose: {
            position: { x: 0, y: 0, z: 0 },
            orientation: { x: 0, y: 0, z: 0, w: 1 },
        },
        scale: { x: 1, y: 1, z: 1 },
        color: { r: 1, g: 1, b: 1, a: 1 },
        points: [],
        colors: [],
        text: "",
        mesh_resource: "",
        mesh_use_embedded_materials: true,
        lifetime: { sec: 0, nsec: 0 },
    },
    schemaName: "visualization_msgs/Marker",
    sizeInBytes: 0,
};
const baseLabel = {
    topic: "/labels",
    receiveTime: { sec: 10, nsec: 0 },
    message: {
        header: { seq: 0, stamp: { sec: 0, nsec: 0 }, frame_id: "" },
        id: 0,
        ns: "",
        type: 9,
        action: 0,
        frame_locked: false,
        pose: {
            position: { x: 0, y: 0, z: 0 },
            orientation: { x: 0, y: 0, z: 0, w: 1 },
        },
        scale: { x: 0, y: 0, z: 0.2 },
        color: { r: 1, g: 1, b: 1, a: 1 },
        points: [],
        colors: [],
        text: "",
        mesh_resource: "",
        mesh_use_embedded_materials: false,
        lifetime: { sec: 0, nsec: 0 },
    },
    schemaName: "visualization_msgs/Marker",
    sizeInBytes: 0,
};
export const ColladaUpAxisObserve = {
    render: function Story() {
        const topics = [
            { name: "/markers", schemaName: "visualization_msgs/Marker" },
            { name: "/labels", schemaName: "visualization_msgs/Marker" },
        ];
        const yup = {
            ...baseMeshMarker,
            message: {
                ...baseMeshMarker.message,
                ns: "yup",
                pose: { position: { x: -1, y: 0, z: 0 }, orientation: { x: 0, y: 0, z: 0, w: 1 } },
                mesh_resource: COLLADA_CONE_Y_UP_MESH_RESOURCE,
            },
        };
        const zup = {
            ...baseMeshMarker,
            message: {
                ...baseMeshMarker.message,
                ns: "zup",
                pose: { position: { x: 1, y: 0, z: 0 }, orientation: { x: 0, y: 0, z: 0, w: 1 } },
                mesh_resource: COLLADA_CONE_Z_UP_MESH_RESOURCE,
            },
        };
        const yupLabel = {
            ...baseLabel,
            message: {
                ...baseLabel.message,
                ns: "yup",
                pose: { position: { x: -1, y: -2, z: 0 }, orientation: { x: 0, y: 0, z: 0, w: 1 } },
                text: "Y-Up",
            },
        };
        const zupLabel = {
            ...baseLabel,
            message: {
                ...baseLabel.message,
                ns: "zup",
                pose: { position: { x: 1, y: -2, z: 0 }, orientation: { x: 0, y: 0, z: 0, w: 1 } },
                text: "Z-Up",
            },
        };
        const fixture = useDelayedFixture({
            topics,
            frame: {
                "/markers": [yup, zup],
                "/labels": [yupLabel, zupLabel],
            },
            capabilities: [],
            activeData: {
                currentTime: { sec: 0, nsec: 0 },
            },
        });
        return (_jsx(PanelSetup, { fixture: fixture, children: _jsx(ThreeDeePanel, { overrideConfig: {
                    layers: {
                        grid: { layerId: "foxglove.Grid" },
                    },
                    scene: {
                        transforms: {
                            showLabel: false,
                        },
                    },
                    cameraState: { ...DEFAULT_CAMERA_STATE, distance: 5, thetaOffset: 50 },
                    topics: {
                        "/markers": { visible: true },
                        "/labels": { visible: true },
                    },
                } }) }));
    },
    parameters: { colorScheme: "dark" },
};
export const ColladaUpAxisIgnore = {
    render: function Story() {
        const topics = [
            { name: "/markers", schemaName: "visualization_msgs/Marker" },
            { name: "/labels", schemaName: "visualization_msgs/Marker" },
        ];
        const yup = {
            ...baseMeshMarker,
            message: {
                ...baseMeshMarker.message,
                ns: "yup",
                pose: { position: { x: -1, y: 0, z: 0 }, orientation: { x: 0, y: 0, z: 0, w: 1 } },
                mesh_resource: COLLADA_CONE_Y_UP_MESH_RESOURCE,
            },
        };
        const zup = {
            ...baseMeshMarker,
            message: {
                ...baseMeshMarker.message,
                ns: "zup",
                pose: { position: { x: 1, y: 0, z: 0 }, orientation: { x: 0, y: 0, z: 0, w: 1 } },
                mesh_resource: COLLADA_CONE_Z_UP_MESH_RESOURCE,
            },
        };
        const yupLabel = {
            ...baseLabel,
            message: {
                ...baseLabel.message,
                ns: "yup",
                pose: { position: { x: -1, y: -2, z: 0 }, orientation: { x: 0, y: 0, z: 0, w: 1 } },
                text: "Y-Up",
            },
        };
        const zupLabel = {
            ...baseLabel,
            message: {
                ...baseLabel.message,
                ns: "zup",
                pose: { position: { x: 1, y: -2, z: 0 }, orientation: { x: 0, y: 0, z: 0, w: 1 } },
                text: "Z-Up",
            },
        };
        const fixture = useDelayedFixture({
            topics,
            frame: {
                "/markers": [yup, zup],
                "/labels": [yupLabel, zupLabel],
            },
            capabilities: [],
            activeData: {
                currentTime: { sec: 0, nsec: 0 },
            },
        });
        return (_jsx(PanelSetup, { fixture: fixture, children: _jsx(ThreeDeePanel, { overrideConfig: {
                    layers: {
                        grid: { layerId: "foxglove.Grid" },
                    },
                    scene: {
                        transforms: {
                            showLabel: false,
                        },
                        ignoreColladaUpAxis: true,
                    },
                    cameraState: { ...DEFAULT_CAMERA_STATE, distance: 5, thetaOffset: 50 },
                    topics: {
                        "/markers": { visible: true },
                        "/labels": { visible: true },
                    },
                } }) }));
    },
    parameters: { colorScheme: "dark" },
};
