// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
//
// This file incorporates work covered by the following copyright and
// permission notice:
//
//   Copyright 2018-2021 Cruise LLC
//
//   This source code is licensed under the Apache License, Version 2.0,
//   found at http://www.apache.org/licenses/LICENSE-2.0
//   You may not use this file except in compliance with the License.
import { PlayerPresence, } from "@foxglove/studio-base/players/types";
export default class FakePlayer {
    #listener;
    playerId = "test";
    subscriptions = [];
    publishers;
    #capabilities = [];
    #profile;
    setListener(listener) {
        this.#listener = listener;
    }
    async emit({ activeData, presence, progress, playerId, } = {}) {
        if (!this.#listener) {
            return undefined;
        }
        await this.#listener({
            playerId: playerId ?? this.playerId,
            presence: presence ?? PlayerPresence.PRESENT,
            capabilities: this.#capabilities,
            profile: this.#profile,
            progress: progress ?? {},
            activeData,
        });
    }
    close = () => {
        // no-op
    };
    setPlaybackSpeed = () => {
        // no-op
    };
    pausePlayback = () => {
        // no-op
    };
    publish = () => {
        // no-op
    };
    callService = async () => {
        // no-op
    };
    setPublishers = (pubs) => {
        this.publishers = pubs;
    };
    setParameter(_key, _value) {
        // no-op
    }
    setSubscriptions = (subs) => {
        this.subscriptions = subs;
    };
    setCapabilities = (capabilities) => {
        this.#capabilities = capabilities;
    };
    setProfile = (profile) => {
        this.#profile = profile;
    };
    startPlayback = () => {
        // no-op
    };
    seekPlayback = () => {
        // no-op
    };
    setGlobalVariables = () => {
        // no-op
    };
}
