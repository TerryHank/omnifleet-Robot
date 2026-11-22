// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { t } from "i18next";
import { PinholeCameraModel } from "@foxglove/den/image";
import Logger from "@foxglove/log";
import { toNanoSec } from "@foxglove/rostime";
import { RenderableLineList } from "./markers/RenderableLineList";
import { cameraInfosEqual, normalizeCameraInfo, projectPixel } from "./projections";
import { Renderable } from "../Renderable";
import { SceneExtension, onlyLastByTopicMessage } from "../SceneExtension";
import { makeRgba, rgbaToCssString, stringToRgba } from "../color";
import { CAMERA_CALIBRATION_DATATYPES } from "../foxglove";
import { CAMERA_INFO_DATATYPES as ROS_CAMERA_INFO_DATATYPES, MarkerAction, MarkerType, TIME_ZERO, } from "../ros";
import { fieldLineWidth, PRECISION_DISTANCE } from "../settings";
import { topicIsConvertibleToSchema } from "../topicIsConvertibleToSchema";
import { makePose } from "../transforms";
const log = Logger.getLogger(__filename);
void log;
const DEFAULT_DISTANCE = 1;
const DEFAULT_PLANAR_PROJECTION_FACTOR = 0;
const DEFAULT_WIDTH = 0.01;
const DEFAULT_COLOR = { r: 124 / 255, g: 107 / 255, b: 1, a: 1 };
const DEFAULT_COLOR_STR = rgbaToCssString(DEFAULT_COLOR);
const CAMERA_MODEL = "CameraModel";
const DEFAULT_SETTINGS = {
    visible: false,
    frameLocked: true,
    distance: DEFAULT_DISTANCE,
    planarProjectionFactor: DEFAULT_PLANAR_PROJECTION_FACTOR,
    width: DEFAULT_WIDTH,
    color: DEFAULT_COLOR_STR,
};
export class CameraInfoRenderable extends Renderable {
    dispose() {
        this.userData.lines?.dispose();
        super.dispose();
    }
    details() {
        return this.userData.originalMessage ?? {};
    }
}
export class Cameras extends SceneExtension {
    static extensionId = "foxglove.Cameras";
    constructor(renderer, name = Cameras.extensionId) {
        super(name, renderer);
    }
    getSubscriptions() {
        return [
            {
                type: "schema",
                schemaNames: ROS_CAMERA_INFO_DATATYPES,
                subscription: { handler: this.#handleCameraInfo, filterQueue: onlyLastByTopicMessage },
            },
            {
                type: "schema",
                schemaNames: CAMERA_CALIBRATION_DATATYPES,
                subscription: { handler: this.#handleCameraInfo, filterQueue: onlyLastByTopicMessage },
            },
        ];
    }
    settingsNodes() {
        const configTopics = this.renderer.config.topics;
        const handler = this.handleSettingsAction;
        const entries = [];
        for (const topic of this.renderer.topics ?? []) {
            if (!(topicIsConvertibleToSchema(topic, ROS_CAMERA_INFO_DATATYPES) ||
                topicIsConvertibleToSchema(topic, CAMERA_CALIBRATION_DATATYPES))) {
                continue;
            }
            const config = (configTopics[topic.name] ?? {});
            const fields = {
                distance: {
                    label: t("threeDee:distance"),
                    input: "number",
                    placeholder: String(DEFAULT_DISTANCE),
                    step: 0.1,
                    precision: PRECISION_DISTANCE,
                    value: config.distance,
                },
                planarProjectionFactor: {
                    label: t("threeDee:planarProjectionFactor"),
                    input: "number",
                    placeholder: String(DEFAULT_PLANAR_PROJECTION_FACTOR),
                    min: 0,
                    max: 1,
                    step: 0.1,
                    precision: 2,
                    value: config.planarProjectionFactor,
                },
                width: fieldLineWidth(t("threeDee:lineWidth"), config.width, DEFAULT_WIDTH),
                color: {
                    label: t("threeDee:color"),
                    input: "rgba",
                    value: config.color ?? DEFAULT_COLOR_STR,
                },
            };
            entries.push({
                path: ["topics", topic.name],
                node: {
                    icon: "Camera",
                    fields,
                    visible: config.visible ?? DEFAULT_SETTINGS.visible,
                    handler,
                    order: topic.name.toLocaleLowerCase(),
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
            const { cameraInfo, receiveTime, originalMessage } = renderable.userData;
            if (cameraInfo) {
                const settings = this.renderer.config.topics[topicName];
                this.#updateCameraInfoRenderable(renderable, cameraInfo, originalMessage, receiveTime, settings);
            }
        }
    };
    #handleCameraInfo = (messageEvent) => {
        const topic = messageEvent.topic;
        const cameraInfo = normalizeCameraInfo(messageEvent.message);
        const receiveTime = toNanoSec(messageEvent.receiveTime);
        let renderable = this.renderables.get(topic);
        if (!renderable) {
            const messageTime = toNanoSec(cameraInfo.header.stamp);
            const frameId = this.renderer.normalizeFrameId(cameraInfo.header.frame_id);
            // Set the initial settings from default values merged with any user settings
            const userSettings = this.renderer.config.topics[topic];
            const settings = { ...DEFAULT_SETTINGS, ...userSettings };
            renderable = new CameraInfoRenderable(topic, this.renderer, {
                receiveTime,
                messageTime,
                frameId,
                pose: makePose(),
                settingsPath: ["topics", topic],
                settings,
                topic,
                cameraInfo: undefined,
                originalMessage: undefined,
                cameraModel: undefined,
                lines: undefined,
            });
            this.add(renderable);
            this.renderables.set(topic, renderable);
        }
        this.#updateCameraInfoRenderable(renderable, cameraInfo, messageEvent.message, receiveTime, renderable.userData.settings);
    };
    #updateCameraInfoRenderable(renderable, cameraInfo, originalMessage, receiveTime, settings) {
        const prevSettings = renderable.userData.settings;
        const newSettings = { ...DEFAULT_SETTINGS, ...settings };
        const settingsEqual = newSettings.color === prevSettings.color &&
            newSettings.distance === prevSettings.distance &&
            newSettings.planarProjectionFactor === prevSettings.planarProjectionFactor &&
            newSettings.width === prevSettings.width;
        const topic = renderable.userData.topic;
        renderable.userData.receiveTime = receiveTime;
        renderable.userData.messageTime = toNanoSec(cameraInfo.header.stamp);
        renderable.userData.frameId = this.renderer.normalizeFrameId(cameraInfo.header.frame_id);
        renderable.userData.settings = newSettings;
        // If the CameraInfo message contents changed, rebuild cameraModel
        const dataEqual = cameraInfosEqual(renderable.userData.cameraInfo, cameraInfo);
        if (!dataEqual) {
            // log.warn(`CameraInfo changed on topic "${topic}", updating rectification model`);
            renderable.userData.cameraInfo = cameraInfo;
            renderable.userData.originalMessage = originalMessage;
            if (cameraInfo.P.length === 12) {
                try {
                    renderable.userData.cameraModel = new PinholeCameraModel(cameraInfo);
                }
                catch (errUnk) {
                    const err = errUnk;
                    this.renderer.settings.errors.addToTopic(topic, CAMERA_MODEL, err.message);
                    renderable.userData.cameraModel = undefined;
                    if (renderable.userData.lines) {
                        renderable.remove(renderable.userData.lines);
                        renderable.userData.lines.dispose();
                        renderable.userData.lines = undefined;
                    }
                }
            }
            else {
                this.renderer.settings.errors.addToTopic(topic, CAMERA_MODEL, `P has length ${cameraInfo.P.length}, not a 3x4 matrix`);
            }
        }
        // If the CameraInfo message contents changed or the settings changed, redraw the wireframe
        if (renderable.userData.cameraModel != undefined &&
            (!dataEqual || !settingsEqual || !renderable.userData.lines)) {
            this.renderer.settings.errors.removeFromTopic(topic, CAMERA_MODEL);
            // Synthesize a LINE_LIST marker to instantiate or update a RenderableLineList
            const marker = createLineListMarker(cameraInfo, renderable.userData.cameraModel, renderable.userData.settings);
            if (!renderable.userData.lines) {
                renderable.userData.lines = new RenderableLineList(topic, marker, undefined, this.renderer);
                renderable.add(renderable.userData.lines);
            }
            else {
                renderable.userData.lines.update(marker, undefined);
            }
        }
    }
}
function vec3() {
    return { x: 0, y: 0, z: 0 };
}
function createLineListMarker(cameraInfo, cameraModel, settings, steps = 10) {
    // Create the four lines from the camera origin to the four corners of the image
    const uv = { x: 0, y: 0 };
    const tl = projectPixel(vec3(), uv, cameraModel, settings);
    uv.x = cameraInfo.width;
    uv.y = 0;
    const tr = projectPixel(vec3(), uv, cameraModel, settings);
    uv.x = 0;
    uv.y = cameraInfo.height;
    const bl = projectPixel(vec3(), uv, cameraModel, settings);
    uv.x = cameraInfo.width;
    uv.y = cameraInfo.height;
    const br = projectPixel(vec3(), uv, cameraModel, settings);
    const origin = { x: 0, y: 0, z: 0 };
    const points = [origin, tl, origin, tr, origin, br, origin, bl];
    // Top-left -> top-right
    points.push(tl);
    horizontalLine(points, 0, cameraInfo, cameraModel, steps, settings);
    points.push(tr);
    // Bottom-left -> bottom-right
    points.push(bl);
    horizontalLine(points, cameraInfo.height, cameraInfo, cameraModel, steps, settings);
    points.push(br);
    // Top-left -> bottom-left
    points.push(tl);
    verticalLine(points, 0, cameraInfo, cameraModel, steps, settings);
    points.push(bl);
    // Top-right -> bottom-right
    points.push(tr);
    verticalLine(points, cameraInfo.width, cameraInfo, cameraModel, steps, settings);
    points.push(br);
    return {
        header: cameraInfo.header,
        ns: "",
        id: 0,
        type: MarkerType.LINE_LIST,
        action: MarkerAction.ADD,
        pose: makePose(),
        scale: { x: settings.width, y: settings.width, z: settings.width },
        color: stringToRgba(makeRgba(), settings.color),
        lifetime: TIME_ZERO,
        frame_locked: true,
        points,
        colors: [],
        text: "",
        mesh_resource: "",
        mesh_use_embedded_materials: false,
    };
}
function horizontalLine(output, y, cameraInfo, cameraModel, steps, settings) {
    const uv = { x: 0, y: 0 };
    for (let i = 1; i < steps; i++) {
        uv.x = (i / steps) * cameraInfo.width;
        uv.y = y;
        const p = projectPixel(vec3(), uv, cameraModel, settings);
        output.push(p, p);
    }
}
function verticalLine(output, x, cameraInfo, cameraModel, steps, settings) {
    const uv = { x: 0, y: 0 };
    for (let i = 1; i < steps; i++) {
        uv.x = x;
        uv.y = (i / steps) * cameraInfo.height;
        const p = projectPixel(vec3(), uv, cameraModel, settings);
        output.push(p, p);
    }
}
