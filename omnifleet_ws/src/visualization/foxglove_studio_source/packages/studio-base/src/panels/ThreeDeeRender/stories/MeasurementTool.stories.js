import { jsx as _jsx } from "react/jsx-runtime";
import PanelSetup from "@foxglove/studio-base/stories/PanelSetup";
import delay from "@foxglove/studio-base/util/delay";
import { QUAT_IDENTITY, rad2deg } from "./common";
import ThreeDeePanel from "../index";
export default {
    title: "panels/ThreeDeeRender",
    component: ThreeDeePanel,
};
export const MeasurementTool = {
    render: function Story() {
        const topics = [{ name: "/tf", schemaName: "geometry_msgs/TransformStamped" }];
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
        const fixture = {
            topics,
            frame: { "/tf": [tf1] },
            capabilities: [],
            activeData: {
                currentTime: { sec: 0, nsec: 0 },
            },
        };
        return (_jsx(PanelSetup, { fixture: fixture, children: _jsx(ThreeDeePanel, { overrideConfig: {
                    ...ThreeDeePanel.defaultConfig,
                    followTf: "base_link",
                    layers: {
                        grid: { layerId: "foxglove.Grid" },
                    },
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
                } }) }));
    },
    parameters: { colorScheme: "dark", chromatic: { delay: 200 } },
    play: async () => {
        document.querySelector("[data-testid=measure-button]").click();
        await delay(100);
        document
            .querySelector("canvas")
            .dispatchEvent(new MouseEvent("mousedown", { clientX: 100, clientY: 100 }));
        document
            .querySelector("canvas")
            .dispatchEvent(new MouseEvent("click", { clientX: 100, clientY: 100 }));
        document
            .querySelector("canvas")
            .dispatchEvent(new MouseEvent("mousedown", { clientX: 300, clientY: 200 }));
        document
            .querySelector("canvas")
            .dispatchEvent(new MouseEvent("click", { clientX: 300, clientY: 200 }));
        await delay(100);
    },
};
