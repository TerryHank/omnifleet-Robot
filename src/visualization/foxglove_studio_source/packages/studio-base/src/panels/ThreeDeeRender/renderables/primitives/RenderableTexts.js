// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { toNanoSec } from "@foxglove/rostime";
import { RenderablePrimitive } from "./RenderablePrimitive";
import { getLuminance, makeRgba, SRGBToLinear, stringToRgba } from "../../color";
const tempRgba = makeRgba();
export class RenderableTexts extends RenderablePrimitive {
    #labelPool;
    #labels = [];
    constructor(renderer) {
        super("", renderer);
        this.#labelPool = renderer.labelPool;
    }
    #ensureCapacity(newLength) {
        const oldLength = this.#labels.length;
        if (newLength > oldLength) {
            for (let i = oldLength; i < newLength; i++) {
                const newLabel = this.#labelPool.acquire();
                this.#labels.push(newLabel);
                this.add(newLabel);
            }
        }
    }
    #updateTexts(texts) {
        this.#ensureCapacity(texts.length);
        const overrideColor = this.userData.settings.color
            ? stringToRgba(tempRgba, this.userData.settings.color)
            : undefined;
        let i = 0;
        for (const text of texts) {
            const color = overrideColor ?? text.color;
            const label = this.#labels[i];
            if (!label) {
                throw new Error("invariant: labels array smaller than requested");
            }
            label.setText(text.text);
            label.setColor(SRGBToLinear(color.r), SRGBToLinear(color.g), SRGBToLinear(color.b), color.a);
            const foregroundIsDark = getLuminance(color.r, color.g, color.b) < 0.5;
            if (foregroundIsDark) {
                label.setBackgroundColor(1, 1, 1, color.a);
            }
            else {
                label.setBackgroundColor(0, 0, 0, color.a);
            }
            label.setLineHeight(text.font_size);
            // note that billboard needs to be true for scale_invariant to work
            label.setBillboard(text.billboard);
            // attenuation -> size accounts for distance from camera
            // scale_invariant negates this and should make it the same size always
            label.setSizeAttenuation(!text.scale_invariant);
            label.quaternion.set(text.pose.orientation.x, text.pose.orientation.y, text.pose.orientation.z, text.pose.orientation.w);
            label.position.set(text.pose.position.x, text.pose.position.y, text.pose.position.z);
            i++;
        }
        // need to release the no longer used labels so that they don't linger on the scene
        if (i < this.#labels.length) {
            // cuts off remaining labels and loops through  them  release to from labelpool
            for (const label of this.#labels.splice(i)) {
                this.#labelPool.release(label);
            }
        }
    }
    dispose() {
        for (const label of this.#labels) {
            this.#labelPool.release(label);
        }
    }
    update(topic, entity, settings, receiveTime) {
        super.update(topic, entity, settings, receiveTime);
        if (entity) {
            const lifetimeNs = toNanoSec(entity.lifetime);
            this.userData.expiresAt = lifetimeNs === 0n ? undefined : receiveTime + lifetimeNs;
            this.#updateTexts(entity.texts);
        }
    }
    updateSettings(settings) {
        this.update(this.userData.topic, this.userData.entity, settings, this.userData.receiveTime);
    }
}
