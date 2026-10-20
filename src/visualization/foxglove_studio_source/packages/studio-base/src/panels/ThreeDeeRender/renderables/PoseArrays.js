// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { t } from "i18next";
import * as _ from "lodash-es";
import { toNanoSec } from "@foxglove/rostime";
import { Axis, AXIS_LENGTH } from "./Axis";
import { createArrowMarker } from "./Poses";
import { RenderableArrow } from "./markers/RenderableArrow";
import { RenderableLineStrip } from "./markers/RenderableLineStrip";
import { Renderable } from "../Renderable";
import { onlyLastByTopicMessage, SceneExtension, } from "../SceneExtension";
import { makeRgba, rgbaGradient, rgbaToCssString, stringToRgba } from "../color";
import { POSES_IN_FRAME_DATATYPES } from "../foxglove";
import { normalizeHeader, normalizePose, normalizeTime } from "../normalizeMessages";
import { POSE_ARRAY_DATATYPES, NAV_PATH_DATATYPES, MarkerType, MarkerAction, } from "../ros";
import { fieldGradient, fieldLineWidth, fieldScaleVec3, fieldSize, } from "../settings";
import { topicIsConvertibleToSchema } from "../topicIsConvertibleToSchema";
import { makePose } from "../transforms";
const DEFAULT_TYPE = "axis";
const DEFAULT_AXIS_SCALE = AXIS_LENGTH;
const DEFAULT_ARROW_SCALE = [1, 0.15, 0.15];
const DEFAULT_LINE_WIDTH = 0.2;
const DEFAULT_GRADIENT = [
    { r: 124 / 255, g: 107 / 255, b: 1, a: 1 },
    { r: 124 / 255, g: 107 / 255, b: 1, a: 0.5 },
];
const MISMATCHED_FRAME_ID = "MISMATCHED_FRAME_ID";
const TIME_ZERO = { sec: 0, nsec: 0 };
const COLOR_WHITE = { r: 1, g: 1, b: 1, a: 1 };
const DEFAULT_GRADIENT_STR = [
    rgbaToCssString(DEFAULT_GRADIENT[0]),
    rgbaToCssString(DEFAULT_GRADIENT[1]),
];
const DEFAULT_SETTINGS = {
    visible: false,
    type: DEFAULT_TYPE,
    axisScale: DEFAULT_AXIS_SCALE,
    arrowScale: DEFAULT_ARROW_SCALE,
    lineWidth: DEFAULT_LINE_WIDTH,
    gradient: DEFAULT_GRADIENT_STR,
};
const tempColor1 = makeRgba();
const tempColor2 = makeRgba();
const tempColor3 = makeRgba();
export class PoseArrayRenderable extends Renderable {
    dispose() {
        this.userData.axes.forEach((axis) => {
            axis.dispose();
        });
        this.userData.arrows.forEach((arrow) => {
            arrow.dispose();
        });
        this.userData.lineStrip?.dispose();
        super.dispose();
    }
    details() {
        return this.userData.originalMessage;
    }
    removeArrows() {
        for (const arrow of this.userData.arrows) {
            this.remove(arrow);
            arrow.dispose();
        }
        this.userData.arrows.length = 0;
    }
    removeAxes() {
        for (const axis of this.userData.axes) {
            this.remove(axis);
            axis.dispose();
        }
        this.userData.axes.length = 0;
    }
    removeLineStrip() {
        if (this.userData.lineStrip) {
            this.remove(this.userData.lineStrip);
            this.userData.lineStrip.dispose();
            this.userData.lineStrip = undefined;
        }
    }
}
export class PoseArrays extends SceneExtension {
    static extensionId = "foxglove.PoseArrays";
    constructor(renderer, name = PoseArrays.extensionId) {
        super(name, renderer);
    }
    getSubscriptions() {
        return [
            {
                type: "schema",
                schemaNames: POSE_ARRAY_DATATYPES,
                subscription: { handler: this.#handlePoseArray, filterQueue: onlyLastByTopicMessage },
            },
            {
                type: "schema",
                schemaNames: POSES_IN_FRAME_DATATYPES,
                subscription: { handler: this.#handlePosesInFrame, filterQueue: onlyLastByTopicMessage },
            },
            {
                type: "schema",
                schemaNames: NAV_PATH_DATATYPES,
                subscription: { handler: this.#handleNavPath, filterQueue: onlyLastByTopicMessage },
            },
        ];
    }
    settingsNodes() {
        const configTopics = this.renderer.config.topics;
        const handler = this.handleSettingsAction;
        const entries = [];
        for (const topic of this.renderer.topics ?? []) {
            if (!(topicIsConvertibleToSchema(topic, POSE_ARRAY_DATATYPES) ||
                topicIsConvertibleToSchema(topic, NAV_PATH_DATATYPES) ||
                topicIsConvertibleToSchema(topic, POSES_IN_FRAME_DATATYPES))) {
                continue;
            }
            const config = (configTopics[topic.name] ?? {});
            const displayType = config.type ?? getDefaultType(topic);
            const { axisScale, lineWidth } = config;
            const arrowScale = config.arrowScale ?? DEFAULT_ARROW_SCALE;
            const gradient = config.gradient ?? DEFAULT_GRADIENT_STR;
            const fields = {
                type: {
                    label: t("threeDee:type"),
                    input: "select",
                    options: [
                        { label: t("threeDee:poseDisplayTypeAxis"), value: "axis" },
                        { label: t("threeDee:poseDisplayTypeArrow"), value: "arrow" },
                        { label: t("threeDee:poseDisplayTypeLine"), value: "line" },
                    ],
                    value: displayType,
                },
            };
            switch (displayType) {
                case "axis":
                    fields["axisScale"] = fieldSize(t("threeDee:scale"), axisScale, DEFAULT_AXIS_SCALE);
                    break;
                case "arrow":
                    fields["arrowScale"] = fieldScaleVec3(t("threeDee:scale"), arrowScale);
                    break;
                case "line":
                    fields["lineWidth"] = fieldLineWidth(t("threeDee:lineWidth"), lineWidth, DEFAULT_LINE_WIDTH);
                    break;
            }
            // Axis does not currently support gradients. This could possibly be done with tinting
            if (displayType !== "axis") {
                fields["gradient"] = fieldGradient(t("threeDee:gradient"), gradient);
            }
            entries.push({
                path: ["topics", topic.name],
                node: {
                    label: topic.name,
                    icon: topicIsConvertibleToSchema(topic, NAV_PATH_DATATYPES) ? "Timeline" : "Flag",
                    fields,
                    visible: config.visible ?? DEFAULT_SETTINGS.visible,
                    handler,
                },
            });
        }
        return entries;
    }
    handleSettingsAction = (action) => {
        const path = action.payload.path;
        if (action.action !== "update" || path.length !== 3) {
            return;
        }
        this.saveSetting(path, action.payload.value);
        // Update the renderable
        const topicName = path[1];
        const renderable = this.renderables.get(topicName);
        if (renderable) {
            const settings = this.renderer.config.topics[topicName];
            const defaultType = { type: getDefaultType(this.renderer.topicsByName?.get(topicName)) };
            this.#updatePoseArrayRenderable(renderable, renderable.userData.poseArrayMessage, renderable.userData.originalMessage, renderable.userData.receiveTime, { ...DEFAULT_SETTINGS, ...defaultType, ...settings });
        }
    };
    #handlePoseArray = (messageEvent) => {
        const poseArrayMessage = normalizePoseArray(messageEvent.message);
        const receiveTime = toNanoSec(messageEvent.receiveTime);
        this.#addPoseArray(messageEvent.topic, poseArrayMessage, messageEvent.message, receiveTime);
    };
    #handleNavPath = (messageEvent) => {
        if (!validateNavPath(messageEvent, this.renderer)) {
            return;
        }
        const poseArrayMessage = normalizeNavPathToPoseArray(messageEvent.message);
        const receiveTime = toNanoSec(messageEvent.receiveTime);
        this.#addPoseArray(messageEvent.topic, poseArrayMessage, messageEvent.message, receiveTime);
    };
    #handlePosesInFrame = (messageEvent) => {
        const poseArrayMessage = normalizePosesInFrameToPoseArray(messageEvent.message);
        const receiveTime = toNanoSec(messageEvent.receiveTime);
        this.#addPoseArray(messageEvent.topic, poseArrayMessage, messageEvent.message, receiveTime);
    };
    #addPoseArray(topic, poseArrayMessage, originalMessage, receiveTime) {
        let renderable = this.renderables.get(topic);
        if (!renderable) {
            // Set the initial settings from default values merged with any user settings
            const userSettings = this.renderer.config.topics[topic];
            const defaultType = { type: getDefaultType(this.renderer.topicsByName?.get(topic)) };
            const settings = { ...DEFAULT_SETTINGS, ...defaultType, ...userSettings };
            renderable = new PoseArrayRenderable(topic, this.renderer, {
                receiveTime,
                messageTime: toNanoSec(poseArrayMessage.header.stamp),
                frameId: this.renderer.normalizeFrameId(poseArrayMessage.header.frame_id),
                pose: makePose(),
                settingsPath: ["topics", topic],
                settings,
                topic,
                poseArrayMessage,
                originalMessage,
                axes: [],
                arrows: [],
            });
            this.add(renderable);
            this.renderables.set(topic, renderable);
        }
        this.#updatePoseArrayRenderable(renderable, poseArrayMessage, originalMessage, receiveTime, renderable.userData.settings);
    }
    #createAxesToMatchPoses(renderable, poseArray, topic) {
        const scale = renderable.userData.settings.axisScale * (1 / AXIS_LENGTH);
        // Update the scale and visibility of existing AxisRenderables as needed
        const existingUpdateCount = Math.min(renderable.userData.axes.length, poseArray.poses.length);
        for (let i = 0; i < existingUpdateCount; i++) {
            const axis = renderable.userData.axes[i];
            axis.visible = true;
            axis.scale.set(scale, scale, scale);
        }
        // Create any AxisRenderables as needed
        for (let i = renderable.userData.axes.length; i < poseArray.poses.length; i++) {
            const axis = new Axis(topic, this.renderer);
            renderable.userData.axes.push(axis);
            renderable.add(axis);
            // Set the scale for each new axis
            axis.scale.set(scale, scale, scale);
        }
        // Hide any AxisRenderables as needed
        for (let i = poseArray.poses.length; i < renderable.userData.axes.length; i++) {
            const axis = renderable.userData.axes[i];
            axis.visible = false;
        }
    }
    #createArrowsToMatchPoses(renderable, poseArray, topic, colorStart, colorEnd) {
        // Generate a Marker with the right scale and color
        const createArrowMarkerFromIndex = (i) => {
            const color = rgbaGradient(tempColor3, colorStart, colorEnd, i / (poseArray.poses.length - 1));
            return createArrowMarker(renderable.userData.settings.arrowScale, color);
        };
        // Update the arrowMarker of existing RenderableArrow as needed
        const existingUpdateCount = Math.min(renderable.userData.arrows.length, poseArray.poses.length);
        for (let i = 0; i < existingUpdateCount; i++) {
            const arrowMarker = createArrowMarkerFromIndex(i);
            const arrow = renderable.userData.arrows[i];
            arrow.visible = true;
            arrow.update(arrowMarker, undefined);
        }
        // Create any RenderableArrow as needed
        for (let i = renderable.userData.arrows.length; i < poseArray.poses.length; i++) {
            const arrowMarker = createArrowMarkerFromIndex(i);
            const arrow = new RenderableArrow(topic, arrowMarker, undefined, this.renderer);
            renderable.userData.arrows.push(arrow);
            renderable.add(arrow);
        }
        // Hide any RenderableArrow as needed
        for (let i = poseArray.poses.length; i < renderable.userData.arrows.length; i++) {
            const arrow = renderable.userData.arrows[i];
            arrow.visible = false;
        }
    }
    #updatePoseArrayRenderable(renderable, poseArrayMessage, originalMessage, receiveTime, settings) {
        renderable.userData.receiveTime = receiveTime;
        renderable.userData.messageTime = toNanoSec(poseArrayMessage.header.stamp);
        renderable.userData.frameId = this.renderer.normalizeFrameId(poseArrayMessage.header.frame_id);
        renderable.userData.poseArrayMessage = poseArrayMessage;
        renderable.userData.originalMessage = originalMessage;
        const { topic, settings: prevSettings } = renderable.userData;
        const axisOrArrowSettingsChanged = settings.type !== prevSettings.type ||
            settings.axisScale !== prevSettings.axisScale ||
            !_.isEqual(settings.arrowScale, prevSettings.arrowScale) ||
            !_.isEqual(settings.gradient, prevSettings.gradient) ||
            (renderable.userData.arrows.length === 0 && renderable.userData.axes.length === 0);
        renderable.userData.settings = settings;
        const colorStart = stringToRgba(tempColor1, settings.gradient[0]);
        const colorEnd = stringToRgba(tempColor2, settings.gradient[1]);
        if (axisOrArrowSettingsChanged) {
            switch (renderable.userData.settings.type) {
                case "axis":
                    renderable.removeArrows();
                    renderable.removeLineStrip();
                    break;
                case "arrow":
                    renderable.removeAxes();
                    renderable.removeLineStrip();
                    break;
                case "line":
                    {
                        renderable.removeArrows();
                        renderable.removeAxes();
                        const lineStripMarker = createLineStripMarker(poseArrayMessage, settings.lineWidth, colorStart, colorEnd);
                        // Create a RenderableLineStrip if needed
                        if (!renderable.userData.lineStrip) {
                            const lineStrip = new RenderableLineStrip(topic, lineStripMarker, undefined, this.renderer);
                            renderable.userData.lineStrip = lineStrip;
                            renderable.add(lineStrip);
                        }
                        renderable.userData.lineStrip.update(lineStripMarker, undefined);
                    }
                    break;
            }
        }
        // Update the pose for each pose renderable
        switch (settings.type) {
            case "axis":
                this.#createAxesToMatchPoses(renderable, poseArrayMessage, topic);
                for (let i = 0; i < poseArrayMessage.poses.length; i++) {
                    setObjectPose(renderable.userData.axes[i], poseArrayMessage.poses[i]);
                }
                break;
            case "arrow":
                this.#createArrowsToMatchPoses(renderable, poseArrayMessage, topic, colorStart, colorEnd);
                for (let i = 0; i < poseArrayMessage.poses.length; i++) {
                    setObjectPose(renderable.userData.arrows[i], poseArrayMessage.poses[i]);
                }
                break;
            case "line": {
                const lineStripMarker = createLineStripMarker(poseArrayMessage, settings.lineWidth, colorStart, colorEnd);
                renderable.userData.lineStrip?.update(lineStripMarker, undefined);
                break;
            }
        }
    }
}
function getDefaultType(topic) {
    return topic != undefined && NAV_PATH_DATATYPES.has(topic.schemaName) ? "line" : DEFAULT_TYPE;
}
function setObjectPose(object, pose) {
    const p = pose.position;
    const q = pose.orientation;
    object.position.set(p.x, p.y, p.z);
    object.quaternion.set(q.x, q.y, q.z, q.w);
    object.updateMatrix();
}
function createLineStripMarker(message, lineWidth, colorStart, colorEnd) {
    // Create a gradient of colors for the line strip
    const colors = [];
    for (let i = 0; i < message.poses.length; i++) {
        colors.push(rgbaGradient(makeRgba(), colorStart, colorEnd, i / (message.poses.length - 1)));
    }
    return {
        header: message.header,
        ns: "",
        id: 0,
        type: MarkerType.LINE_STRIP,
        action: MarkerAction.ADD,
        pose: makePose(),
        scale: { x: lineWidth, y: 1, z: 1 },
        color: COLOR_WHITE,
        lifetime: TIME_ZERO,
        frame_locked: true,
        points: message.poses.map((pose) => pose.position),
        colors,
        text: "",
        mesh_resource: "",
        mesh_use_embedded_materials: false,
    };
}
function normalizePoseArray(poseArray) {
    return {
        header: normalizeHeader(poseArray.header),
        poses: poseArray.poses?.map((p) => normalizePose(p)) ?? [],
    };
}
function normalizeNavPathToPoseArray(navPath) {
    return {
        header: normalizeHeader(navPath.header),
        poses: navPath.poses?.map((p) => normalizePose(p?.pose)) ?? [],
    };
}
function normalizePosesInFrameToPoseArray(poseArray) {
    return {
        header: { stamp: normalizeTime(poseArray.timestamp), frame_id: poseArray.frame_id ?? "" },
        poses: poseArray.poses?.map(normalizePose) ?? [],
    };
}
function validateNavPath(messageEvent, renderer) {
    const { topic, message: navPath } = messageEvent;
    if (navPath.poses) {
        const baseFrameId = renderer.normalizeFrameId(navPath.header?.frame_id ?? "");
        for (const pose of navPath.poses) {
            const curFrameId = renderer.normalizeFrameId(pose?.header?.frame_id ?? "");
            if (baseFrameId !== curFrameId) {
                renderer.settings.errors.addToTopic(topic, MISMATCHED_FRAME_ID, `Path poses must all have the same frame_id. "${baseFrameId}" != "${curFrameId}"`);
                return false;
            }
        }
    }
    return true;
}
