// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { t } from "i18next";
import * as THREE from "three";
import { filterMap } from "@foxglove/den/collection";
import { onlyLastByTopicMessage } from "@foxglove/studio-base/panels/ThreeDeeRender/SceneExtension";
import { RenderableTopicAnnotations } from "./RenderableTopicAnnotations";
import { IMAGE_ANNOTATIONS_DATATYPES } from "../../../foxglove";
import { IMAGE_MARKER_ARRAY_DATATYPES, IMAGE_MARKER_DATATYPES } from "../../../ros";
import { topicIsConvertibleToSchema } from "../../../topicIsConvertibleToSchema";
import { sortPrefixMatchesToFront } from "../../Images/topicPrefixMatching";
const MISSING_SYNCHRONIZED_ANNOTATION = "MISSING_SYNCHRONIZED_ANNOTATION";
/** For backwards compatibility with previously published type definitions, older studio versions, and webviz */
const LEGACY_ANNOTATION_SCHEMAS = new Set([
    "foxglove_msgs/ImageMarkerArray",
    "foxglove_msgs/msg/ImageMarkerArray",
    "studio_msgs/ImageMarkerArray",
    "studio_msgs/msg/ImageMarkerArray",
    "webviz_msgs/ImageMarkerArray",
]);
const ALL_SUPPORTED_ANNOTATION_SCHEMAS = new Set([
    ...IMAGE_ANNOTATIONS_DATATYPES,
    ...IMAGE_MARKER_DATATYPES,
    ...IMAGE_MARKER_ARRAY_DATATYPES,
    ...LEGACY_ANNOTATION_SCHEMAS,
]);
/**
 * This class handles settings and rendering for ImageAnnotations/ImageMarkers.
 */
export class ImageAnnotations extends THREE.Object3D {
    #context;
    #renderablesByTopic = new Map();
    #cameraModel;
    #scale;
    #canvasWidth;
    #canvasHeight;
    #pixelRatio;
    supportedAnnotationSchemas = ALL_SUPPORTED_ANNOTATION_SCHEMAS;
    constructor(context) {
        super();
        this.#context = context;
        this.#scale = context.initialScale;
        this.#canvasWidth = context.initialCanvasWidth;
        this.#canvasHeight = context.initialCanvasHeight;
        this.#pixelRatio = context.initialPixelRatio;
        context.messageHandler.addListener(this.#updateFromMessageState);
    }
    getSubscriptions() {
        return [
            {
                type: "schema",
                schemaNames: ALL_SUPPORTED_ANNOTATION_SCHEMAS,
                subscription: {
                    handler: this.#context.messageHandler.handleAnnotations,
                    filterQueue: this.#filterMessageQueue.bind(this),
                },
            },
        ];
    }
    handleTopicsChanged(topics) {
        if (!topics) {
            return;
        }
        const availableAnnotationTopics = filterMap(topics, (topic) => {
            if (topicIsConvertibleToSchema(topic, ALL_SUPPORTED_ANNOTATION_SCHEMAS)) {
                return topic.name;
            }
            return undefined;
        });
        this.#context.messageHandler.setAvailableAnnotationTopics(availableAnnotationTopics);
    }
    #filterMessageQueue(msgs) {
        // if sync annotations not active, only take the last message for each topic
        if (this.#context.config().synchronize !== true) {
            return onlyLastByTopicMessage(msgs);
        }
        return msgs;
    }
    dispose() {
        for (const renderable of this.#renderablesByTopic.values()) {
            renderable.dispose();
        }
        this.children.length = 0;
        this.#renderablesByTopic.clear();
    }
    /** Called when seeking or a new data source is loaded.  */
    removeAllRenderables() {
        for (const renderable of this.#renderablesByTopic.values()) {
            renderable.dispose();
            this.remove(renderable);
        }
        this.#renderablesByTopic.clear();
    }
    updateScale(scale, canvasWidth, canvasHeight, pixelRatio) {
        this.#scale = scale;
        this.#canvasWidth = canvasWidth;
        this.#canvasHeight = canvasHeight;
        this.#pixelRatio = pixelRatio;
        for (const renderable of this.#renderablesByTopic.values()) {
            renderable.setScale(scale, canvasWidth, canvasHeight, pixelRatio);
            renderable.update();
        }
    }
    updateCameraModel(cameraModel) {
        this.#cameraModel = cameraModel;
        for (const renderable of this.#renderablesByTopic.values()) {
            renderable.setCameraModel(cameraModel);
            renderable.update();
        }
    }
    #updateFromMessageState = (newState) => {
        if (newState.annotationsByTopic != undefined) {
            for (const { originalMessage, annotations } of newState.annotationsByTopic.values()) {
                this.#handleMessage(originalMessage, annotations);
                // Hide any remaining errors for annotations we are able to render
                this.#context.removeSettingsError(["imageAnnotations", originalMessage.topic], MISSING_SYNCHRONIZED_ANNOTATION);
            }
        }
        for (const topic of newState.presentAnnotationTopics ?? []) {
            // Even if a full synchronized set is not found, hide errors for annotations that were present
            this.#context.removeSettingsError(["imageAnnotations", topic], MISSING_SYNCHRONIZED_ANNOTATION);
        }
        for (const topic of newState.missingAnnotationTopics ?? []) {
            this.#context.addSettingsError(["imageAnnotations", topic], MISSING_SYNCHRONIZED_ANNOTATION, "Waiting for annotation message with timestamp matching image. Turn off “Sync annotations” to display annotations regardless of timestamp.");
        }
        if (newState.missingAnnotationTopics) {
            this.removeAllRenderables();
        }
    };
    #handleMessage(messageEvent, annotations) {
        let renderable = this.#renderablesByTopic.get(messageEvent.topic);
        if (!renderable) {
            renderable = new RenderableTopicAnnotations(messageEvent.topic, this.#context.labelPool);
            renderable.setScale(this.#scale, this.#canvasWidth, this.#canvasHeight, this.#pixelRatio);
            renderable.setCameraModel(this.#cameraModel);
            this.#renderablesByTopic.set(messageEvent.topic, renderable);
            this.add(renderable);
        }
        renderable.setOriginalMessage(messageEvent.message);
        renderable.setAnnotations(annotations);
        renderable.update();
    }
    #handleSettingsAction(action) {
        if (action.action !== "update" || action.payload.path.length < 2) {
            return;
        }
        const { value, path } = action.payload;
        const category = path[0];
        if (category !== "imageAnnotations") {
            return;
        }
        if (path[2] === "visible" && typeof value === "boolean") {
            const topic = path[1];
            this.#handleTopicVisibilityChange(topic, value);
        }
        this.#context.updateSettingsTree();
    }
    #handleTopicVisibilityChange(topic, visible) {
        this.#context.updateConfig((draft) => {
            draft.annotations ??= {};
            const settings = (draft.annotations[topic] ??= {});
            settings.visible = visible;
        });
        this.#context.messageHandler.setConfig(this.#context.config());
        const renderable = this.#renderablesByTopic.get(topic);
        if (renderable) {
            renderable.visible = visible;
        }
    }
    settingsNodes() {
        const entries = [];
        entries.push({
            path: ["imageAnnotations"],
            node: {
                label: t("threeDee:imageAnnotations"),
                enableVisibilityFilter: true,
                defaultExpansionState: "expanded",
            },
        });
        const config = this.#context.config();
        const annotationTopics = this.#context
            .topics()
            .filter((topic) => topicIsConvertibleToSchema(topic, ALL_SUPPORTED_ANNOTATION_SCHEMAS));
        // Sort annotation topics with prefixes matching the image topic to the top.
        if (config.imageTopic) {
            sortPrefixMatchesToFront(annotationTopics, config.imageTopic, (topic) => topic.name);
        }
        for (const topic of annotationTopics) {
            const settings = config.annotations?.[topic.name];
            entries.push({
                path: ["imageAnnotations", topic.name],
                node: {
                    label: topic.name,
                    visible: settings?.visible ?? false,
                    handler: this.#handleSettingsAction.bind(this),
                },
            });
        }
        return entries;
    }
}
