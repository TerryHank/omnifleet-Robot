// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { Renderable } from "@foxglove/studio-base/panels/ThreeDeeRender/Renderable";
import { emptyPose } from "@foxglove/studio-base/util/Pose";
const PRIMITIVE_DEFAULT_SETTINGS = {
    showOutlines: true,
    visible: false,
    color: undefined,
    selectedIdVariable: undefined,
};
export class RenderablePrimitive extends Renderable {
    constructor(name, renderer, userData = {
        receiveTime: -1n,
        messageTime: -1n,
        frameId: "",
        pose: emptyPose(),
        settings: PRIMITIVE_DEFAULT_SETTINGS,
        settingsPath: [],
        entity: undefined,
    }) {
        super(name, renderer, userData);
    }
    update(topic, entity, settings, receiveTime) {
        this.userData.topic = topic;
        this.userData.entity = entity;
        this.userData.settings = settings;
        this.userData.receiveTime = receiveTime;
    }
    idFromMessage() {
        return this.userData.entity?.id;
    }
    selectedIdVariable() {
        const settings = this.getSettings();
        return settings?.selectedIdVariable;
    }
    getSettings() {
        if (this.userData.topic == undefined) {
            return undefined;
        }
        return this.userData.settings;
    }
    details() {
        return this.userData.entity ?? {};
    }
    setColorScheme(colorScheme) {
        void colorScheme;
    }
    prepareForReuse() {
        this.userData.entity = undefined;
        this.userData.pose = emptyPose();
    }
    addError(errorId, message) {
        this.renderer.settings.errors.add(this.userData.settingsPath, errorId, message);
    }
    clearErrors() {
        // presumably a renderable has not been assigned a settings path if it is 0
        // running clearPath([]) will clear all errors from the settings tree
        if (this.userData.settingsPath.length > 0) {
            this.renderer.settings.errors.clearPath(this.userData.settingsPath);
        }
    }
}
