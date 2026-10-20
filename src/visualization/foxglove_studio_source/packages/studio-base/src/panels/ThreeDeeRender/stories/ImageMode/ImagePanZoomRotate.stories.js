import { jsx as _jsx } from "react/jsx-runtime";
import { fireEvent } from "@storybook/testing-library";
import * as THREE from "three";
import { makeRawImageAndCalibration } from "@foxglove/studio-base/panels/ThreeDeeRender/stories/ImageMode/imageCommon";
import PanelSetup from "@foxglove/studio-base/stories/PanelSetup";
import { ImagePanel } from "../../index";
export default {
    title: "panels/ThreeDeeRender/Images/PanZoomRotate",
    component: ImagePanel,
    parameters: { colorScheme: "light" },
};
const BaseStory = ({ rotation, flipHorizontal, flipVertical }) => {
    const width = 60;
    const height = 45;
    const { calibrationMessage, cameraMessage } = makeRawImageAndCalibration({
        width,
        height,
        frameId: "camera",
        imageTopic: "camera",
        calibrationTopic: "calibration",
        // use fx≠fy to test that stretched images are handled correctly when panning and zooming
        fx: 500,
        fy: 700,
    });
    const annotationsMessage = {
        topic: "annotations",
        receiveTime: { sec: 10, nsec: 0 },
        message: {
            circles: [
                {
                    timestamp: { sec: 0, nsec: 0 },
                    position: { x: 10, y: 5 },
                    diameter: 2,
                    thickness: 0.5,
                    fill_color: { r: 1, g: 0, b: 1, a: 1 },
                    outline_color: { r: 1, g: 1, b: 0, a: 1 },
                },
            ],
        },
        schemaName: "foxglove.ImageAnnotations",
        sizeInBytes: 0,
    };
    const sceneUpdateMessage = {
        topic: "scene",
        receiveTime: { sec: 10, nsec: 0 },
        message: {
            entities: [
                {
                    timestamp: { sec: 10, nsec: 0 },
                    frame_id: "camera",
                    id: "x",
                    lifetime: { sec: 0, nsec: 0 },
                    frame_locked: true,
                    metadata: [],
                    arrows: [],
                    cubes: [
                        {
                            pose: {
                                position: { x: 2, y: 1.5, z: 50 },
                                orientation: new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), Math.PI / 4),
                            },
                            color: { r: 1, g: 1, b: 0, a: 0.5 },
                            size: { x: 1, y: 1, z: 1 },
                        },
                    ],
                    spheres: [],
                    cylinders: [],
                    lines: [],
                    triangles: [],
                    texts: [],
                    models: [],
                },
            ],
        },
        schemaName: "foxglove.SceneUpdate",
        sizeInBytes: 0,
    };
    const fixture = {
        topics: [
            { name: "calibration", schemaName: "foxglove.CameraCalibration" },
            { name: "camera", schemaName: "foxglove.RawImage" },
            { name: "annotations", schemaName: "foxglove.ImageAnnotations" },
            { name: "scene", schemaName: "foxglove.SceneUpdate" },
        ],
        frame: {
            calibration: [calibrationMessage],
            camera: [cameraMessage],
            annotations: [annotationsMessage],
            scene: [sceneUpdateMessage],
        },
        capabilities: [],
        activeData: {
            currentTime: { sec: 0, nsec: 0 },
        },
    };
    return (
    // Use a fixed-size container to make the canvas size/position consistent for mouse interactions
    _jsx("div", { style: { width: 800, height: 600, flex: "0 0 auto" }, children: _jsx(PanelSetup, { fixture: fixture, includeSettings: true, settingsWidth: 338, children: _jsx(ImagePanel, { overrideConfig: {
                    ...ImagePanel.defaultConfig,
                    imageMode: {
                        calibrationTopic: "calibration",
                        imageTopic: "camera",
                        annotations: { annotations: { visible: true } },
                        rotation,
                        flipHorizontal,
                        flipVertical,
                    },
                    topics: {
                        scene: { visible: true },
                    },
                } }) }) }));
};
function makeMouseMarker(parent) {
    const mouseMarker = document.createElement("div");
    mouseMarker.style.position = "absolute";
    mouseMarker.style.width = "10px";
    mouseMarker.style.height = "10px";
    mouseMarker.style.borderRadius = "5px";
    mouseMarker.style.backgroundColor = "green";
    parent.appendChild(mouseMarker);
    return mouseMarker;
}
export const PanZoom = {
    render: BaseStory,
    args: {
        dx: 79,
        dy: 189,
        panX: 100,
        panY: 50,
        rotation: 0,
        flipHorizontal: false,
        flipVertical: false,
    },
    play: async ({ args, canvasElement }) => {
        const canvas = document.querySelector("canvas");
        const rect = canvas.getBoundingClientRect();
        const mouseMarker = makeMouseMarker(canvasElement);
        const cx = rect.left + args.dx;
        const cy = rect.top + args.dy;
        function setMarkerPos(x, y) {
            mouseMarker.style.left = `${x - 5}px`;
            mouseMarker.style.top = `${y - 5}px`;
        }
        setMarkerPos(cx, cy);
        fireEvent.mouseDown(canvas, { clientX: cx, clientY: cy });
        setMarkerPos(cx + args.panX, cy + args.panY);
        fireEvent.mouseMove(canvas, { clientX: cx + args.panX, clientY: cy + args.panY });
        fireEvent.mouseUp(canvas, { clientX: cx + args.panX, clientY: cy + args.panY });
        fireEvent.wheel(canvas, { clientX: cx + args.panX, clientY: cy + args.panY, deltaY: 100 });
        // pan again after zooming to ensure the zoom scale is accounted for
        fireEvent.mouseDown(canvas, { clientX: cx + args.panX, clientY: cy + args.panY });
        setMarkerPos(cx + args.panX * 0.3, cy + args.panY * 0.3);
        fireEvent.mouseMove(canvas, { clientX: cx + args.panX * 0.3, clientY: cy + args.panY * 0.3 });
        fireEvent.mouseUp(canvas, { clientX: cx + args.panX * 0.3, clientY: cy + args.panY * 0.3 });
    },
};
export const PanZoomFlipH = {
    ...PanZoom,
    args: {
        dx: 387,
        dy: 189,
        panX: -100,
        panY: 50,
        rotation: 0,
        flipHorizontal: true,
        flipVertical: false,
    },
};
export const PanZoomFlipV = {
    ...PanZoom,
    args: {
        dx: 79,
        dy: 382,
        panX: 100,
        panY: 50,
        rotation: 0,
        flipHorizontal: false,
        flipVertical: true,
    },
};
export const PanZoom90 = {
    ...PanZoom,
    args: {
        dx: 352,
        dy: 96,
        panX: 100,
        panY: 50,
        rotation: 90,
        flipHorizontal: false,
        flipVertical: false,
    },
};
export const PanZoom90FlipH = {
    ...PanZoom,
    args: {
        dx: 115,
        dy: 96,
        panX: 100,
        panY: 50,
        rotation: 90,
        flipHorizontal: true,
        flipVertical: false,
    },
};
export const PanZoom90FlipV = {
    ...PanZoom,
    args: {
        dx: 352,
        dy: 476,
        panX: -100,
        panY: -50,
        rotation: 90,
        flipHorizontal: false,
        flipVertical: true,
    },
};
export const PanZoom180 = {
    ...PanZoom,
    args: {
        dx: 387,
        dy: 382,
        panX: -100,
        panY: 50,
        rotation: 180,
        flipHorizontal: false,
        flipVertical: false,
    },
};
export const PanZoom270 = {
    ...PanZoom,
    args: {
        dx: 115,
        dy: 476,
        panX: 100,
        panY: -50,
        rotation: 270,
        flipHorizontal: false,
        flipVertical: false,
    },
};
