// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { toNanoSec } from "@foxglove/rostime";
import { RenderableLineStrip } from "./markers/RenderableLineStrip";
import { Renderable } from "../Renderable";
import { SceneExtension, onlyLastByTopicMessage, } from "../SceneExtension";
import { makeRgba, rgbaToCssString, stringToRgba } from "../color";
import { normalizeHeader, normalizeVector3s } from "../normalizeMessages";
import { MarkerAction, MarkerType, POLYGON_STAMPED_DATATYPES, TIME_ZERO, } from "../ros";
import { topicIsConvertibleToSchema } from "../topicIsConvertibleToSchema";
import { makePose } from "../transforms";
const DEFAULT_COLOR = { r: 124 / 255, g: 107 / 255, b: 1, a: 1 };
const DEFAULT_LINE_WIDTH = 0.1;
const DEFAULT_COLOR_STR = rgbaToCssString(DEFAULT_COLOR);
const DEFAULT_SETTINGS = {
    visible: false,
    lineWidth: DEFAULT_LINE_WIDTH,
    color: DEFAULT_COLOR_STR,
};
export class PolygonRenderable extends Renderable {
    dispose() {
        this.userData.lines?.dispose();
        super.dispose();
    }
    details() {
        return this.userData.polygonStamped;
    }
}
export class Polygons extends SceneExtension {
    static extensionId = "foxglove.Polygons";
    constructor(renderer, name = Polygons.extensionId) {
        super(name, renderer);
    }
    getSubscriptions() {
        return [
            {
                type: "schema",
                schemaNames: POLYGON_STAMPED_DATATYPES,
                subscription: { handler: this.#handlePolygon, filterQueue: onlyLastByTopicMessage },
            },
        ];
    }
    settingsNodes() {
        const configTopics = this.renderer.config.topics;
        const handler = this.handleSettingsAction;
        const entries = [];
        for (const topic of this.renderer.topics ?? []) {
            if (!topicIsConvertibleToSchema(topic, POLYGON_STAMPED_DATATYPES)) {
                continue;
            }
            const config = (configTopics[topic.name] ?? {});
            // prettier-ignore
            const fields = {
                lineWidth: { label: "线宽", input: "number", min: 0, placeholder: String(DEFAULT_LINE_WIDTH), step: 0.005, precision: 3, value: config.lineWidth },
                color: { label: "颜色", input: "rgba", value: config.color ?? DEFAULT_COLOR_STR },
            };
            entries.push({
                path: ["topics", topic.name],
                node: {
                    label: topic.name,
                    icon: "Star",
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
            renderable.userData.settings = { ...DEFAULT_SETTINGS, ...settings };
            this.#updatePolygonRenderable(renderable, renderable.userData.polygonStamped, renderable.userData.receiveTime);
        }
    };
    #handlePolygon = (messageEvent) => {
        const topic = messageEvent.topic;
        const polygonStamped = normalizePolygonStamped(messageEvent.message);
        const receiveTime = toNanoSec(messageEvent.receiveTime);
        let renderable = this.renderables.get(topic);
        if (!renderable) {
            // Set the initial settings from default values merged with any user settings
            const userSettings = this.renderer.config.topics[topic];
            const settings = { ...DEFAULT_SETTINGS, ...userSettings };
            renderable = new PolygonRenderable(topic, this.renderer, {
                receiveTime,
                messageTime: toNanoSec(polygonStamped.header.stamp),
                frameId: this.renderer.normalizeFrameId(polygonStamped.header.frame_id),
                pose: makePose(),
                settingsPath: ["topics", topic],
                settings,
                topic,
                polygonStamped,
                lines: undefined,
            });
            this.add(renderable);
            this.renderables.set(topic, renderable);
        }
        this.#updatePolygonRenderable(renderable, polygonStamped, receiveTime);
    };
    #updatePolygonRenderable(renderable, polygonStamped, receiveTime) {
        const settings = renderable.userData.settings;
        renderable.userData.receiveTime = receiveTime;
        renderable.userData.messageTime = toNanoSec(polygonStamped.header.stamp);
        renderable.userData.frameId = this.renderer.normalizeFrameId(polygonStamped.header.frame_id);
        renderable.userData.polygonStamped = polygonStamped;
        const topic = renderable.userData.topic;
        const linesMarker = createLineStripMarker(polygonStamped, settings);
        if (!renderable.userData.lines) {
            renderable.userData.lines = new RenderableLineStrip(topic, linesMarker, receiveTime, this.renderer);
            renderable.add(renderable.userData.lines);
        }
        else {
            renderable.userData.lines.update(linesMarker, receiveTime);
        }
    }
}
function createLineStripMarker(polygonStamped, settings) {
    // Close the polygon
    const points = [...polygonStamped.polygon.points];
    if (points.length > 0) {
        points.push(points[0]);
    }
    const linesMarker = {
        header: polygonStamped.header,
        ns: "",
        id: 0,
        type: MarkerType.LINE_STRIP,
        action: MarkerAction.ADD,
        pose: makePose(),
        scale: { x: settings.lineWidth, y: 1, z: 1 },
        color: stringToRgba(makeRgba(), settings.color),
        lifetime: TIME_ZERO,
        frame_locked: true,
        points,
        colors: [],
        text: "",
        mesh_resource: "",
        mesh_use_embedded_materials: false,
    };
    return linesMarker;
}
function normalizePolygon(polygon) {
    return {
        points: normalizeVector3s(polygon?.points),
    };
}
function normalizePolygonStamped(polygon) {
    return {
        header: normalizeHeader(polygon.header),
        polygon: normalizePolygon(polygon.polygon),
    };
}
