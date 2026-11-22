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
export var ImageMarkerType;
(function (ImageMarkerType) {
    ImageMarkerType[ImageMarkerType["CIRCLE"] = 0] = "CIRCLE";
    ImageMarkerType[ImageMarkerType["LINE_STRIP"] = 1] = "LINE_STRIP";
    ImageMarkerType[ImageMarkerType["LINE_LIST"] = 2] = "LINE_LIST";
    ImageMarkerType[ImageMarkerType["POLYGON"] = 3] = "POLYGON";
    ImageMarkerType[ImageMarkerType["POINTS"] = 4] = "POINTS";
    // TEXT is not part of visualization_msgs/ImageMarker, but we include it to
    // support existing frameworks that have extended this message definition
    ImageMarkerType[ImageMarkerType["TEXT"] = 5] = "TEXT";
})(ImageMarkerType || (ImageMarkerType = {}));
export var ImageMarkerAction;
(function (ImageMarkerAction) {
    ImageMarkerAction[ImageMarkerAction["ADD"] = 0] = "ADD";
    ImageMarkerAction[ImageMarkerAction["REMOVE"] = 1] = "REMOVE";
})(ImageMarkerAction || (ImageMarkerAction = {}));
