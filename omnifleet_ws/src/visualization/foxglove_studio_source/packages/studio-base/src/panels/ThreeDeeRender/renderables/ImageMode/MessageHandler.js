// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import * as _ from "lodash-es";
import { AVLTree } from "@foxglove/avl";
import { fromNanoSec, toNanoSec, compare as compareTime, isLessThan, } from "@foxglove/rostime";
import { getTimestampFromImage, } from "@foxglove/studio-base/panels/ThreeDeeRender/renderables/Images/ImageTypes";
import { normalizeCompressedImage, normalizeRawImage, normalizeRosCompressedImage, normalizeRosImage, } from "@foxglove/studio-base/panels/ThreeDeeRender/renderables/Images/imageNormalizers";
import { normalizeCameraInfo } from "@foxglove/studio-base/panels/ThreeDeeRender/renderables/projections";
import { normalizeAnnotations } from "./annotations/normalizeAnnotations";
import { IMAGE_MODE_HUD_GROUP_ID, WAITING_FOR_BOTH_MESSAGES_HUD_ID, WAITING_FOR_CALIBRATION_HUD_ID, WAITING_FOR_IMAGES_NOTICE_ID, WAITING_FOR_IMAGES_EMPTY_HUD_ID, WAITING_FOR_SYNC_NOTICE_HUD_ID, WAITING_FOR_SYNC_EMPTY_HUD_ID, } from "./constants";
import { t3D } from "../../t3D";
// Have constants for the HUD items so that they don't need to be recreated and GCed every message
export const WAITING_FOR_BOTH_HUD_ITEM = {
    id: WAITING_FOR_BOTH_MESSAGES_HUD_ID,
    group: IMAGE_MODE_HUD_GROUP_ID,
    getMessage: () => t3D("waitingForCalibrationAndImages"),
    displayType: "empty",
};
export const WAITING_FOR_CALIBRATION_HUD_ITEM = {
    id: WAITING_FOR_CALIBRATION_HUD_ID,
    group: IMAGE_MODE_HUD_GROUP_ID,
    getMessage: () => t3D("waitingForCalibration"),
    displayType: "empty",
};
export const WAITING_FOR_IMAGE_NOTICE_HUD_ITEM = {
    id: WAITING_FOR_IMAGES_NOTICE_ID,
    group: IMAGE_MODE_HUD_GROUP_ID,
    getMessage: () => t3D("waitingForImages"),
    displayType: "notice",
};
export const WAITING_FOR_IMAGE_EMPTY_HUD_ITEM = {
    id: WAITING_FOR_IMAGES_EMPTY_HUD_ID,
    group: IMAGE_MODE_HUD_GROUP_ID,
    getMessage: () => t3D("waitingForImages"),
    displayType: "empty",
};
export const WAITING_FOR_SYNC_NOTICE_HUD_ITEM = {
    id: WAITING_FOR_SYNC_NOTICE_HUD_ID,
    group: IMAGE_MODE_HUD_GROUP_ID,
    getMessage: () => t3D("waitingForSyncAnnotations"),
    displayType: "notice",
};
export const WAITING_FOR_SYNC_EMPTY_HUD_ITEM = {
    id: WAITING_FOR_SYNC_EMPTY_HUD_ID,
    group: IMAGE_MODE_HUD_GROUP_ID,
    getMessage: () => t3D("waitingForSyncAnnotations"),
    displayType: "empty",
};
/**
 * Processes and normalizes incoming messages and manages state of
 * messages to be rendered given the ImageMode config. A large part of this responsibility
 * is managing state in synchronized mode and ensuring that the a synchronized set of image and
 * annotations are handed off to the SceneExtension for rendering.
 */
export class MessageHandler {
    /** settings that should reflect image mode config */
    #config;
    /** Allows message handler push messages to overlay on top of the canvas */
    #hud;
    /** last state passed to listeners */
    #oldRenderState;
    /** internal state of last received messages */
    #lastReceivedMessages;
    /** sorted tree that holds state for synchronized messages. Used to find most recent synchronized set of image and annotations. */
    #tree;
    /** listener functions that are called when the state changes. */
    #listeners = [];
    /** Holds what annotations are currently available on the given source. These are needed because annotations
     * that are marked as visible may be present in the layout/config, but are not present on the source.
     * This can cause synchronized annotations to never resolve if the source does not have the annotation topic
     * with no indication to the user that the annotation is not available.
     */
    #availableAnnotationTopics;
    /**
     *
     * @param config - subset of ImageMode settings required for message handling
     */
    constructor(config, hud) {
        this.#config = config;
        this.#hud = hud;
        this.#lastReceivedMessages = {
            annotationsByTopic: new Map(),
        };
        this.#tree = new AVLTree(compareTime);
        this.#availableAnnotationTopics = new Set();
    }
    addListener(listener) {
        this.#listeners.push(listener);
    }
    removeListener(listener) {
        this.#listeners = this.#listeners.filter((fn) => fn !== listener);
    }
    handleRosRawImage = (messageEvent) => {
        this.handleImage(messageEvent, normalizeRosImage(messageEvent.message));
    };
    handleRosCompressedImage = (messageEvent) => {
        this.handleImage(messageEvent, normalizeRosCompressedImage(messageEvent.message));
    };
    handleRawImage = (messageEvent) => {
        this.handleImage(messageEvent, normalizeRawImage(messageEvent.message));
    };
    handleCompressedImage = (messageEvent) => {
        this.handleImage(messageEvent, normalizeCompressedImage(messageEvent.message));
    };
    handleImage(message, image) {
        const normalizedImageMessage = {
            ...message,
            message: image,
        };
        this.#lastReceivedMessages.image = normalizedImageMessage;
        if (this.#config.synchronize !== true) {
            this.#emitState();
            return;
        }
        // Update the image at the stamp time
        this.#addImageToTree(normalizedImageMessage);
        this.#emitState();
    }
    #addImageToTree(normalizedImageMessage) {
        const image = normalizedImageMessage.message;
        const item = this.#tree.get(getTimestampFromImage(image));
        if (item) {
            item.image = normalizedImageMessage;
        }
        else {
            this.#tree.set(getTimestampFromImage(image), {
                image: normalizedImageMessage,
                annotationsByTopic: new Map(),
            });
        }
    }
    handleCameraInfo = (message) => {
        const cameraInfo = normalizeCameraInfo(message.message);
        this.#lastReceivedMessages.cameraInfo = cameraInfo;
        this.#emitState();
    };
    handleAnnotations = (messageEvent) => {
        const annotations = normalizeAnnotations(messageEvent.message, messageEvent.schemaName);
        const { topic } = messageEvent;
        if (this.#config.synchronize !== true) {
            this.#lastReceivedMessages.annotationsByTopic.set(topic, {
                originalMessage: messageEvent,
                annotations,
            });
            this.#emitState();
            return;
        }
        const groups = new Map();
        for (const annotation of annotations) {
            const key = toNanoSec(annotation.stamp);
            const arr = groups.get(key);
            if (arr) {
                arr.push(annotation);
                continue;
            }
            groups.set(key, [annotation]);
        }
        for (const [stampNsec, group] of groups) {
            const stamp = fromNanoSec(stampNsec);
            let item = this.#tree.get(stamp);
            if (!item) {
                item = {
                    image: undefined,
                    annotationsByTopic: new Map(),
                };
                this.#tree.set(stamp, item);
            }
            item.annotationsByTopic.set(topic, {
                originalMessage: messageEvent,
                annotations: group,
            });
        }
        this.#emitState();
    };
    setConfig(newConfig) {
        let changed = false;
        if (newConfig.synchronize != undefined && newConfig.synchronize !== this.#config.synchronize) {
            this.#oldRenderState = undefined;
            this.#tree.clear();
            if (newConfig.synchronize && this.#lastReceivedMessages.image != undefined) {
                this.#addImageToTree(this.#lastReceivedMessages.image);
            }
            changed = true;
        }
        if ("imageTopic" in newConfig && this.#config.imageTopic !== newConfig.imageTopic) {
            for (const item of this.#tree.values()) {
                item.image = undefined;
            }
            this.#lastReceivedMessages.image = undefined;
            changed = true;
        }
        if (this.#config.calibrationTopic !== newConfig.calibrationTopic) {
            this.#lastReceivedMessages.cameraInfo = undefined;
            changed = true;
        }
        if (newConfig.annotations != undefined &&
            this.#config.annotations &&
            this.#config.annotations !== newConfig.annotations) {
            const newVisibleTopics = new Set();
            for (const [topic, settings] of Object.entries(newConfig.annotations)) {
                if (settings?.visible === true) {
                    newVisibleTopics.add(topic);
                }
            }
            for (const topic of this.#lastReceivedMessages.annotationsByTopic.keys()) {
                if (!newVisibleTopics.has(topic)) {
                    this.#lastReceivedMessages.annotationsByTopic.delete(topic);
                    changed = true;
                }
            }
            for (const syncEntry of this.#tree.values()) {
                for (const topic of syncEntry.annotationsByTopic.keys()) {
                    if (!newVisibleTopics.has(topic)) {
                        syncEntry.annotationsByTopic.delete(topic);
                        changed = true;
                    }
                }
            }
        }
        this.#config = newConfig;
        if (changed) {
            this.#emitState();
        }
    }
    setAvailableAnnotationTopics(topicNames) {
        this.#availableAnnotationTopics = new Set(topicNames);
        this.#emitState();
    }
    clear() {
        this.#lastReceivedMessages = {
            annotationsByTopic: new Map(),
        };
        this.#tree.clear();
        this.#oldRenderState = undefined;
        this.#emitState();
    }
    #emitState() {
        const state = this.getRenderStateAndUpdateHUD();
        this.#listeners.forEach((fn) => {
            fn(state, this.#oldRenderState);
        });
        this.#oldRenderState = state;
    }
    /** Do not use. only public for testing */
    getRenderStateAndUpdateHUD() {
        const state = this.#getRenderState();
        this.#updateHUDFromState(state);
        return state;
    }
    #updateHUDFromState(state) {
        const calibrationRequired = this.#config.calibrationTopic != undefined;
        const waitingForImage = this.#lastReceivedMessages.image == undefined && state.image == undefined;
        const waitingForCalibration = calibrationRequired && state.cameraInfo == undefined;
        const waitingForBoth = waitingForImage && waitingForCalibration;
        this.#hud.displayIfTrue(waitingForBoth, WAITING_FOR_BOTH_HUD_ITEM);
        // don't show other empty states when waiting for both to reduce noise
        this.#hud.displayIfTrue(waitingForCalibration && !waitingForBoth, WAITING_FOR_CALIBRATION_HUD_ITEM);
        this.#hud.displayIfTrue(waitingForImage && !calibrationRequired && !waitingForBoth, WAITING_FOR_IMAGE_EMPTY_HUD_ITEM);
        this.#hud.displayIfTrue(waitingForImage && calibrationRequired, WAITING_FOR_IMAGE_NOTICE_HUD_ITEM);
        const waitingForSync = !!state.missingAnnotationTopics && state.missingAnnotationTopics.length > 0;
        this.#hud.displayIfTrue(waitingForSync && calibrationRequired, WAITING_FOR_SYNC_NOTICE_HUD_ITEM);
        // it is an empty state if calibration not required
        this.#hud.displayIfTrue(waitingForSync && !calibrationRequired, WAITING_FOR_SYNC_EMPTY_HUD_ITEM);
    }
    #getRenderState() {
        if (this.#config.synchronize === true) {
            const result = findSynchronizedSetAndRemoveOlderItems(this.#tree, this.#visibleAnnotations());
            if (result.found) {
                return {
                    cameraInfo: this.#lastReceivedMessages.cameraInfo,
                    image: result.messages.image,
                    annotationsByTopic: result.messages.annotationsByTopic,
                };
            }
            return {
                cameraInfo: this.#lastReceivedMessages.cameraInfo,
                presentAnnotationTopics: result.presentAnnotationTopics,
                missingAnnotationTopics: result.missingAnnotationTopics,
            };
        }
        return { ...this.#lastReceivedMessages };
    }
    #visibleAnnotations() {
        const visibleAnnotations = new Set();
        for (const [topic, settings] of Object.entries(this.#config.annotations ?? {})) {
            if (settings?.visible === true && this.#availableAnnotationTopics.has(topic)) {
                visibleAnnotations.add(topic);
            }
        }
        return visibleAnnotations;
    }
}
/**
 * Find the newest entry where we have everything synchronized and remove all older entries from tree.
 * @param tree - AVL tree that stores a [image?, annotations?] in sorted order by timestamp.
 * @param visibleAnnotations - visible annotation topics
 * @returns - the newest synchronized item with all active annotations and image, or set of missing annotations if synchronization failed
 */
function findSynchronizedSetAndRemoveOlderItems(tree, visibleAnnotations) {
    let validEntry = undefined;
    let presentAnnotationTopics;
    let missingAnnotationTopics;
    for (const entry of tree.entries()) {
        const messageState = entry[1];
        if (!messageState.image) {
            continue;
        }
        [presentAnnotationTopics, missingAnnotationTopics] = _.partition(Array.from(visibleAnnotations), (topic) => messageState.annotationsByTopic.has(topic));
        // If we have an image and all the messages for annotation topics then we have a synchronized set.
        if (missingAnnotationTopics.length === 0) {
            validEntry = entry;
        }
    }
    if (validEntry) {
        // We've got a set of synchronized messages, remove any older items from the tree
        let minKey = tree.minKey();
        while (minKey && isLessThan(minKey, validEntry[0])) {
            tree.shift();
            minKey = tree.minKey();
        }
        return { found: true, messages: validEntry[1] };
    }
    return { found: false, missingAnnotationTopics, presentAnnotationTopics };
}
