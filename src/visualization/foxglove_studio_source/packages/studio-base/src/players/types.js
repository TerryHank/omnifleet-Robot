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
export var PlayerPresence;
(function (PlayerPresence) {
    PlayerPresence["NOT_PRESENT"] = "NOT_PRESENT";
    PlayerPresence["INITIALIZING"] = "INITIALIZING";
    PlayerPresence["RECONNECTING"] = "RECONNECTING";
    PlayerPresence["BUFFERING"] = "BUFFERING";
    PlayerPresence["PRESENT"] = "PRESENT";
    PlayerPresence["ERROR"] = "ERROR";
})(PlayerPresence || (PlayerPresence = {}));
// Capabilities that are not shared by all players.
export const PlayerCapabilities = {
    // Publishing messages. Need to be connected to some sort of live robotics system (e.g. ROS).
    advertise: "advertise",
    // Fetching assets.
    assets: "assets",
    // Calling services
    callServices: "callServices",
    // Setting speed to something that is not real time.
    setSpeed: "setSpeed",
    // Ability to play, pause, and seek in time.
    playbackControl: "playbackControl",
    // List and retrieve values for configuration key/value pairs
    getParameters: "getParameters",
    // Set values for configuration key/value pairs
    setParameters: "setParameters",
};
