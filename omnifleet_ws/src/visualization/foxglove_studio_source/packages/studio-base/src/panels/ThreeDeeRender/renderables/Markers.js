// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { t } from "i18next";
import * as _ from "lodash-es";
import { toNanoSec } from "@foxglove/rostime";
import { TopicMarkers } from "./TopicMarkers";
import { SELECTED_ID_VARIABLE } from "../Renderable";
import { SceneExtension } from "../SceneExtension";
import { normalizeColorRGBA, normalizeColorRGBAs, normalizeHeader, normalizePose, normalizeTime, normalizeVector3, normalizeVector3s, } from "../normalizeMessages";
import { MARKER_ARRAY_DATATYPES, MARKER_DATATYPES } from "../ros";
import { topicIsConvertibleToSchema } from "../topicIsConvertibleToSchema";
import { makePose } from "../transforms";
const DEFAULT_SETTINGS = {
    visible: false,
    showOutlines: true,
    color: undefined,
    selectedIdVariable: undefined,
    namespaces: {},
};
export class Markers extends SceneExtension {
    static extensionId = "foxglove.Markers";
    constructor(renderer, name = Markers.extensionId) {
        super(name, renderer);
    }
    getSubscriptions() {
        return [
            {
                type: "schema",
                schemaNames: MARKER_ARRAY_DATATYPES,
                subscription: { handler: this.#handleMarkerArray },
            },
            {
                type: "schema",
                schemaNames: MARKER_DATATYPES,
                subscription: { handler: this.#handleMarker },
            },
        ];
    }
    settingsNodes() {
        const configTopics = this.renderer.config.topics;
        const entries = [];
        for (const topic of this.renderer.topics ?? []) {
            if (!(topicIsConvertibleToSchema(topic, MARKER_ARRAY_DATATYPES) ||
                topicIsConvertibleToSchema(topic, MARKER_DATATYPES))) {
                continue;
            }
            const config = (configTopics[topic.name] ?? {});
            const node = {
                label: topic.name,
                icon: "Shapes",
                order: topic.name.toLocaleLowerCase(),
                fields: {
                    color: { label: t("threeDee:color"), input: "rgba", value: config.color },
                    showOutlines: {
                        label: t("threeDee:showOutline"),
                        input: "boolean",
                        value: config.showOutlines ?? DEFAULT_SETTINGS.showOutlines,
                    },
                    selectedIdVariable: {
                        label: t("threeDee:selectionVariable"),
                        input: "string",
                        help: t("threeDee:selectionVariableHelp"),
                        value: config.selectedIdVariable,
                        placeholder: SELECTED_ID_VARIABLE,
                    },
                },
                visible: config.visible ?? DEFAULT_SETTINGS.visible,
                handler: this.handleSettingsAction,
            };
            // Create a list of all the namespaces for this topic
            const topicMarkers = this.renderables.get(topic.name);
            const namespaces = Array.from(topicMarkers?.namespaces.values() ?? []).sort((a, b) => a.namespace.localeCompare(b.namespace));
            if (namespaces.length > 1 || (namespaces.length === 1 && namespaces[0].namespace !== "")) {
                node.children = {};
                for (const ns of namespaces) {
                    const child = {
                        label: ns.namespace !== "" ? ns.namespace : `""`,
                        icon: "Shapes",
                        visible: ns.settings.visible,
                        defaultExpansionState: namespaces.length > 1 ? "collapsed" : "expanded",
                        handler: this.#handleSettingsActionNamespace,
                    };
                    node.children[`ns:${ns.namespace}`] = child;
                }
            }
            entries.push({ path: ["topics", topic.name], node });
        }
        return entries;
    }
    startFrame(currentTime, renderFrameId, fixedFrameId) {
        // Don't use SceneExtension#startFrame() because our renderables represent one topic each with
        // many markers. Instead, call startFrame on each renderable
        for (const renderable of this.renderables.values()) {
            renderable.startFrame(currentTime, renderFrameId, fixedFrameId);
        }
    }
    handleSettingsAction = (action) => {
        const path = action.payload.path;
        if (action.action !== "update" || path.length !== 3) {
            return;
        }
        this.saveSetting(path, action.payload.value);
        // Update the TopicMarkers settings
        const topicName = path[1];
        const topicMarkers = this.renderables.get(topicName);
        if (topicMarkers) {
            const settings = this.renderer.config.topics[topicName];
            topicMarkers.userData.settings = { ...DEFAULT_SETTINGS, ...settings };
            topicMarkers.update();
        }
    };
    #handleSettingsActionNamespace = (action) => {
        const path = action.payload.path;
        if (action.action !== "update" || path.length !== 4) {
            return;
        }
        const topicName = path[1];
        const namespaceKey = path[2];
        const fieldName = path[3];
        const namespace = namespaceKey.slice(3); // remove `ns:` prefix
        this.renderer.updateConfig((draft) => {
            // We build the settings tree with paths of the form
            //   ["topics", <topic>, "ns:"<namespace>, "visible"]
            // but the config is stored with paths of the form
            //   ["topics", <topic>, "namespaces", <namespace>, "visible"]
            const actualPath = ["topics", topicName, "namespaces", namespace, fieldName];
            _.set(draft, actualPath, action.payload.value);
        });
        // Update the MarkersNamespace settings
        const renderable = this.renderables.get(topicName);
        if (renderable) {
            const settings = this.renderer.config.topics[topicName];
            const ns = renderable.namespaces.get(namespace);
            if (ns) {
                const nsSettings = settings?.namespaces?.[namespace];
                ns.settings = { ...ns.settings, ...nsSettings };
            }
        }
        // Update the settings sidebar
        this.updateSettingsTree();
    };
    #handleMarkerArray = (messageEvent) => {
        const topic = messageEvent.topic;
        const markerArray = messageEvent.message;
        const receiveTime = toNanoSec(messageEvent.receiveTime);
        for (const markerMsg of markerArray.markers ?? []) {
            if (markerMsg) {
                const marker = normalizeMarker(markerMsg);
                this.#addMarker(topic, marker, receiveTime);
            }
        }
    };
    #handleMarker = (messageEvent) => {
        const topic = messageEvent.topic;
        const marker = normalizeMarker(messageEvent.message);
        const receiveTime = toNanoSec(messageEvent.receiveTime);
        this.#addMarker(topic, marker, receiveTime);
    };
    #addMarker(topic, marker, receiveTime) {
        const topicMarkers = this.#getTopicMarkers(topic, marker, receiveTime);
        const prevNsCount = topicMarkers.namespaces.size;
        topicMarkers.addMarkerMessage(marker, receiveTime);
        // If the topic has a new namespace, rebuild the settings node for this topic
        if (prevNsCount !== topicMarkers.namespaces.size) {
            this.updateSettingsTree();
        }
    }
    addMarkerArray(topic, markerArray, receiveTime) {
        const firstMarker = markerArray[0];
        if (!firstMarker) {
            return;
        }
        const topicMarkers = this.#getTopicMarkers(topic, firstMarker, receiveTime);
        const prevNsCount = topicMarkers.namespaces.size;
        for (const marker of markerArray) {
            topicMarkers.addMarkerMessage(marker, receiveTime);
        }
        // If the topic has a new namespace, rebuild the settings node for this topic
        if (prevNsCount !== topicMarkers.namespaces.size) {
            this.updateSettingsTree();
        }
    }
    #getTopicMarkers(topic, marker, receiveTime) {
        let topicMarkers = this.renderables.get(topic);
        if (!topicMarkers) {
            const userSettings = this.renderer.config.topics[topic];
            topicMarkers = new TopicMarkers(topic, this.renderer, {
                receiveTime,
                messageTime: toNanoSec(marker.header.stamp),
                frameId: this.renderer.normalizeFrameId(marker.header.frame_id),
                pose: makePose(),
                settingsPath: ["topics", topic],
                topic,
                settings: { ...DEFAULT_SETTINGS, ...userSettings },
            });
            this.renderables.set(topic, topicMarkers);
            this.add(topicMarkers);
        }
        return topicMarkers;
    }
}
function normalizeMarker(marker) {
    return {
        header: normalizeHeader(marker.header),
        ns: marker.ns ?? "",
        id: marker.id ?? 0,
        type: marker.type ?? 0,
        action: marker.action ?? 0,
        pose: normalizePose(marker.pose),
        scale: normalizeVector3(marker.scale),
        color: normalizeColorRGBA(marker.color),
        lifetime: normalizeTime(marker.lifetime),
        frame_locked: marker.frame_locked ?? false,
        points: normalizeVector3s(marker.points),
        colors: normalizeColorRGBAs(marker.colors),
        text: marker.text ?? "",
        mesh_resource: marker.mesh_resource ?? "",
        mesh_use_embedded_materials: marker.mesh_use_embedded_materials ?? false,
    };
}
