// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import * as _ from "lodash-es";
export function openSiblingPlotPanel(openSiblingPanel, topicName) {
    openSiblingPanel({
        panelType: "Plot",
        updateIfExists: true,
        siblingConfigCreator: (config) => ({
            ...config,
            paths: _.uniq(config.paths
                .concat([{ value: topicName, enabled: true, timestampMethod: "receiveTime" }])
                .filter(({ value }) => value)),
        }),
    });
}
