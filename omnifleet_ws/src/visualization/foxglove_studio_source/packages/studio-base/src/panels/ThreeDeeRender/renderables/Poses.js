// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { t } from "i18next";
import * as _ from "lodash-es";
import { toNanoSec } from "@foxglove/rostime";
import { Axis, AXIS_LENGTH } from "./Axis";
import { RenderableArrow } from "./markers/RenderableArrow";
import { RenderableSphere } from "./markers/RenderableSphere";
import { Renderable } from "../Renderable";
import { onlyLastByTopicMessage, SceneExtension, } from "../SceneExtension";
import { makeRgba, rgbaToCssString, stringToRgba } from "../color";
import { POSE_IN_FRAME_DATATYPES } from "../foxglove";
import { normalizeHeader, normalizeMatrix6, normalizePose, normalizeTime, } from "../normalizeMessages";
import { POSE_WITH_COVARIANCE_STAMPED_DATATYPES, MarkerAction, MarkerType, TIME_ZERO, POSE_STAMPED_DATATYPES, } from "../ros";
import { PRECISION_DISTANCE } from "../settings";
import { topicIsConvertibleToSchema } from "../topicIsConvertibleToSchema";
import { makePose } from "../transforms";
const DEFAULT_TYPE = "axis";
const DEFAULT_AXIS_SCALE = AXIS_LENGTH;
const DEFAULT_ARROW_SCALE = [1, 0.15, 0.15];
const DEFAULT_COLOR = { r: 124 / 255, g: 107 / 255, b: 1, a: 1 };
const DEFAULT_SHOW_COVARIANCE = true;
const DEFAULT_COVARIANCE_COLOR = { r: 198 / 255, g: 107 / 255, b: 1, a: 0.25 };
const DEFAULT_COLOR_STR = rgbaToCssString(DEFAULT_COLOR);
const DEFAULT_COVARIANCE_COLOR_STR = rgbaToCssString(DEFAULT_COVARIANCE_COLOR);
const DEFAULT_SETTINGS = {
    type: DEFAULT_TYPE,
    visible: false,
    axisScale: DEFAULT_AXIS_SCALE,
    arrowScale: DEFAULT_ARROW_SCALE,
    color: DEFAULT_COLOR_STR,
    showCovariance: DEFAULT_SHOW_COVARIANCE,
    covarianceColor: DEFAULT_COVARIANCE_COLOR_STR,
};
export class PoseRenderable extends Renderable {
    dispose() {
        this.userData.axis?.dispose();
        this.userData.arrow?.dispose();
        this.userData.sphere?.dispose();
        super.dispose();
    }
    details() {
        return this.userData.originalMessage;
    }
}
export class Poses extends SceneExtension {
    static extensionId = "foxglove.Poses";
    constructor(renderer, name = Poses.extensionId) {
        super(name, renderer);
    }
    getSubscriptions() {
        return [
            {
                type: "schema",
                schemaNames: POSE_STAMPED_DATATYPES,
                subscription: { handler: this.#handlePoseStamped, filterQueue: onlyLastByTopicMessage },
            },
            {
                type: "schema",
                schemaNames: POSE_IN_FRAME_DATATYPES,
                subscription: { handler: this.#handlePoseInFrame, filterQueue: onlyLastByTopicMessage },
            },
            {
                type: "schema",
                schemaNames: POSE_WITH_COVARIANCE_STAMPED_DATATYPES,
                subscription: {
                    handler: this.#handlePoseWithCovariance,
                    filterQueue: onlyLastByTopicMessage,
                },
            },
        ];
    }
    settingsNodes() {
        const configTopics = this.renderer.config.topics;
        const handler = this.handleSettingsAction;
        const entries = [];
        for (const topic of this.renderer.topics ?? []) {
            const isPoseStamped = topicIsConvertibleToSchema(topic, POSE_STAMPED_DATATYPES);
            const isPoseInFrame = topicIsConvertibleToSchema(topic, POSE_IN_FRAME_DATATYPES);
            const isPoseWithCovarianceStamped = isPoseStamped
                ? false
                : topicIsConvertibleToSchema(topic, POSE_WITH_COVARIANCE_STAMPED_DATATYPES);
            if (!(isPoseStamped || isPoseWithCovarianceStamped || isPoseInFrame)) {
                continue;
            }
            const config = (configTopics[topic.name] ?? {});
            const type = config.type ?? DEFAULT_TYPE;
            const fields = {
                type: {
                    label: t("threeDee:type"),
                    input: "select",
                    options: [
                        { label: t("threeDee:poseDisplayTypeAxis"), value: "axis" },
                        { label: t("threeDee:poseDisplayTypeArrow"), value: "arrow" },
                    ],
                    value: type,
                },
            };
            if (type === "axis") {
                fields["axisScale"] = {
                    label: t("threeDee:scale"),
                    input: "number",
                    step: 0.5,
                    min: 0,
                    precision: PRECISION_DISTANCE,
                    value: config.axisScale ?? DEFAULT_AXIS_SCALE,
                };
            }
            else {
                fields["arrowScale"] = {
                    label: t("threeDee:scale"),
                    input: "vec3",
                    labels: ["X", "Y", "Z"],
                    step: 0.5,
                    precision: PRECISION_DISTANCE,
                    value: config.arrowScale ?? DEFAULT_ARROW_SCALE,
                };
                fields["color"] = {
                    label: t("threeDee:color"),
                    input: "rgba",
                    value: config.color ?? DEFAULT_COLOR_STR,
                };
            }
            if (isPoseWithCovarianceStamped) {
                const showCovariance = config.showCovariance ?? DEFAULT_SHOW_COVARIANCE;
                const covarianceColor = config.covarianceColor ?? DEFAULT_COVARIANCE_COLOR_STR;
                fields["showCovariance"] = {
                    label: t("threeDee:covariance"),
                    input: "boolean",
                    value: showCovariance,
                };
                if (showCovariance) {
                    fields["covarianceColor"] = {
                        label: t("threeDee:covarianceColor"),
                        input: "rgba",
                        value: covarianceColor,
                    };
                }
            }
            entries.push({
                path: ["topics", topic.name],
                node: {
                    label: topic.name,
                    icon: "Flag",
                    fields,
                    visible: config.visible ?? DEFAULT_SETTINGS.visible,
                    order: topic.name.toLocaleLowerCase(),
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
            this.#updatePoseRenderable(renderable, renderable.userData.poseMessage, renderable.userData.originalMessage, renderable.userData.receiveTime, { ...DEFAULT_SETTINGS, ...settings });
        }
    };
    #handlePoseStamped = (messageEvent) => {
        const poseMessage = normalizePoseStamped(messageEvent.message);
        const receiveTime = toNanoSec(messageEvent.receiveTime);
        this.#addPose(messageEvent.topic, poseMessage, messageEvent.message, receiveTime);
    };
    #handlePoseInFrame = (messageEvent) => {
        const poseMessage = normalizePoseInFrameToPoseStamped(messageEvent.message);
        const receiveTime = toNanoSec(messageEvent.receiveTime);
        this.#addPose(messageEvent.topic, poseMessage, messageEvent.message, receiveTime);
    };
    #handlePoseWithCovariance = (messageEvent) => {
        const poseMessage = normalizePoseWithCovarianceStamped(messageEvent.message);
        const receiveTime = toNanoSec(messageEvent.receiveTime);
        this.#addPose(messageEvent.topic, poseMessage, messageEvent.message, receiveTime);
    };
    #addPose(topic, poseMessage, originalMessage, receiveTime) {
        let renderable = this.renderables.get(topic);
        if (!renderable) {
            // Set the initial settings from default values merged with any user settings
            const userSettings = this.renderer.config.topics[topic];
            const settings = { ...DEFAULT_SETTINGS, ...userSettings };
            renderable = new PoseRenderable(topic, this.renderer, {
                receiveTime,
                messageTime: toNanoSec(poseMessage.header.stamp),
                frameId: this.renderer.normalizeFrameId(poseMessage.header.frame_id),
                pose: makePose(),
                settingsPath: ["topics", topic],
                settings,
                topic,
                poseMessage,
                originalMessage,
                axis: undefined,
                arrow: undefined,
                sphere: undefined,
            });
            this.add(renderable);
            this.renderables.set(topic, renderable);
        }
        this.#updatePoseRenderable(renderable, poseMessage, originalMessage, receiveTime, renderable.userData.settings);
    }
    #updatePoseRenderable(renderable, poseMessage, originalMessage, receiveTime, settings) {
        renderable.userData.receiveTime = receiveTime;
        renderable.userData.messageTime = toNanoSec(poseMessage.header.stamp);
        renderable.userData.frameId = this.renderer.normalizeFrameId(poseMessage.header.frame_id);
        renderable.userData.poseMessage = poseMessage;
        renderable.userData.originalMessage = originalMessage;
        // Default the covariance sphere to hidden. If showCovariance is set and a valid covariance
        // matrix is present, it will be shown
        if (renderable.userData.sphere) {
            renderable.userData.sphere.visible = false;
        }
        const { topic, settings: prevSettings } = renderable.userData;
        const axisOrArrowSettingsChanged = settings.type !== prevSettings.type ||
            settings.axisScale !== prevSettings.axisScale ||
            !_.isEqual(settings.arrowScale, prevSettings.arrowScale) ||
            settings.color !== prevSettings.color ||
            (!renderable.userData.arrow && !renderable.userData.axis);
        renderable.userData.settings = settings;
        if (axisOrArrowSettingsChanged) {
            if (renderable.userData.settings.type === "axis") {
                if (renderable.userData.arrow) {
                    renderable.remove(renderable.userData.arrow);
                    renderable.userData.arrow.dispose();
                    renderable.userData.arrow = undefined;
                }
                // Create an AxisRenderable if needed
                if (!renderable.userData.axis) {
                    const axis = new Axis(topic, this.renderer);
                    renderable.userData.axis = axis;
                    renderable.add(axis);
                }
                const scale = renderable.userData.settings.axisScale * (1 / AXIS_LENGTH);
                renderable.userData.axis.scale.set(scale, scale, scale);
            }
            else {
                if (renderable.userData.axis) {
                    renderable.remove(renderable.userData.axis);
                    renderable.userData.axis.dispose();
                    renderable.userData.axis = undefined;
                }
                const color = stringToRgba(makeRgba(), settings.color);
                const arrowMarker = createArrowMarker(settings.arrowScale, color);
                // Create a RenderableArrow if needed
                if (!renderable.userData.arrow) {
                    const arrow = new RenderableArrow(topic, arrowMarker, undefined, this.renderer);
                    renderable.userData.arrow = arrow;
                    renderable.add(arrow);
                }
                renderable.userData.arrow.update(arrowMarker, undefined);
            }
        }
        if ("covariance" in poseMessage.pose) {
            renderable.userData.pose = poseMessage.pose.pose;
            const poseWithCovariance = poseMessage;
            const sphereMarker = createSphereMarker(poseWithCovariance, renderable.userData.settings);
            if (sphereMarker) {
                if (!renderable.userData.sphere) {
                    renderable.userData.sphere = new RenderableSphere(renderable.userData.topic, sphereMarker, undefined, this.renderer);
                    renderable.add(renderable.userData.sphere);
                }
                renderable.userData.sphere.visible = renderable.userData.settings.showCovariance;
                renderable.userData.sphere.update(sphereMarker, undefined);
            }
            else if (renderable.userData.sphere) {
                renderable.userData.sphere.visible = false;
            }
        }
        else {
            renderable.userData.pose = poseMessage.pose;
        }
    }
}
export function createArrowMarker(arrowScale, color) {
    const [x, y, z] = arrowScale;
    return {
        header: { frame_id: "", stamp: { sec: 0, nsec: 0 } },
        ns: "",
        id: 0,
        type: MarkerType.ARROW,
        action: MarkerAction.ADD,
        pose: makePose(),
        scale: { x, y, z },
        color,
        lifetime: TIME_ZERO,
        frame_locked: true,
        points: [],
        colors: [],
        text: "",
        mesh_resource: "",
        mesh_use_embedded_materials: false,
    };
}
function createSphereMarker(poseMessage, settings) {
    // Covariance is a 6x6 matrix for position and rotation (XYZ, RPY)
    // We currently only visualize position variance so extract the upper-left
    // 3x1 diagonal
    // [X, -, -, -, -, -]
    // [-, Y, -, -, -, -]
    // [-, -, Z, -, -, -]
    // [-, -, -, -, -, -]
    // [-, -, -, -, -, -]
    // [-, -, -, -, -, -]
    const K = poseMessage.pose.covariance;
    const scale = { x: Math.sqrt(K[0]), y: Math.sqrt(K[7]), z: Math.sqrt(K[14]) };
    return {
        header: poseMessage.header,
        ns: "",
        id: 1,
        type: MarkerType.SPHERE,
        action: MarkerAction.ADD,
        pose: makePose(),
        scale,
        color: stringToRgba(makeRgba(), settings.covarianceColor),
        lifetime: TIME_ZERO,
        frame_locked: true,
        points: [],
        colors: [],
        text: "",
        mesh_resource: "",
        mesh_use_embedded_materials: false,
    };
}
function normalizePoseStamped(pose) {
    return {
        header: normalizeHeader(pose.header),
        pose: normalizePose(pose.pose),
    };
}
function normalizePoseInFrameToPoseStamped(pose) {
    return {
        header: { stamp: normalizeTime(pose.timestamp), frame_id: pose.frame_id ?? "" },
        pose: normalizePose(pose.pose),
    };
}
function normalizePoseWithCovariance(pose) {
    const covariance = normalizeMatrix6(pose?.covariance);
    return { pose: normalizePose(pose?.pose), covariance };
}
function normalizePoseWithCovarianceStamped(message) {
    return {
        header: normalizeHeader(message.header),
        pose: normalizePoseWithCovariance(message.pose),
    };
}
