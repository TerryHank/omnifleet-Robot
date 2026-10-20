// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { t } from "i18next";
import * as _ from "lodash-es";
import { SceneExtension } from "../SceneExtension";
export const DEFAULT_PUBLISH_SETTINGS = {
    type: "point",
    poseTopic: "/move_base_simple/goal",
    pointTopic: "/clicked_point",
    poseEstimateTopic: "/initialpose",
    poseEstimateXDeviation: 0.5,
    poseEstimateYDeviation: 0.5,
    poseEstimateThetaDeviation: _.round(Math.PI / 12, 8),
};
export class PublishSettings extends SceneExtension {
    static extensionId = "foxglove.PublishSettings";
    constructor(renderer, name = PublishSettings.extensionId) {
        super(name, renderer);
        renderer.publishClickTool.addEventListener("foxglove.publish-type-change", this.#handlePublishToolChange);
    }
    dispose() {
        this.renderer.publishClickTool.removeEventListener("foxglove.publish-type-change", this.#handlePublishToolChange);
        super.dispose();
    }
    settingsNodes() {
        const config = this.renderer.config;
        const { publish } = config;
        const handler = this.handleSettingsAction;
        return [
            {
                path: ["publish"],
                node: {
                    label: t("threeDee:publish"),
                    fields: {
                        type: {
                            label: t("threeDee:type"),
                            input: "select",
                            value: publish.type,
                            options: [
                                { label: t("threeDee:publishTypePoint"), value: "point" },
                                { label: t("threeDee:publishTypePose"), value: "pose" },
                                {
                                    label: t("threeDee:publishTypePoseEstimate"),
                                    value: "pose_estimate",
                                },
                            ],
                            help: t("threeDee:publishTypeHelp"),
                        },
                        topic: {
                            label: t("threeDee:topic"),
                            input: "string",
                            value: {
                                point: publish.pointTopic,
                                pose: publish.poseTopic,
                                pose_estimate: publish.poseEstimateTopic,
                            }[publish.type],
                            help: t("threeDee:publishTopicHelp"),
                        },
                        ...(publish.type === "pose_estimate" && {
                            poseEstimateXDeviation: {
                                label: t("threeDee:xDeviation"),
                                input: "number",
                                value: publish.poseEstimateXDeviation,
                                help: t("threeDee:xDeviationHelp"),
                            },
                            poseEstimateYDeviation: {
                                label: t("threeDee:yDeviation"),
                                input: "number",
                                value: publish.poseEstimateYDeviation,
                                help: t("threeDee:yDeviationHelp"),
                            },
                            poseEstimateThetaDeviation: {
                                label: t("threeDee:thetaDeviation"),
                                input: "number",
                                value: publish.poseEstimateThetaDeviation,
                                help: t("threeDee:thetaDeviationHelp"),
                            },
                        }),
                    },
                    defaultExpansionState: "collapsed",
                    handler,
                },
            },
        ];
    }
    handleSettingsAction = (action) => {
        if (action.action !== "update" || action.payload.path.length === 0) {
            return;
        }
        const path = action.payload.path;
        const category = path[0];
        const value = action.payload.value;
        if (category === "publish") {
            // Update the configuration
            if (path[1] === "topic") {
                this.renderer.updateConfig((draft) => {
                    switch (draft.publish.type) {
                        case "point":
                            draft.publish.pointTopic =
                                value ?? DEFAULT_PUBLISH_SETTINGS.pointTopic;
                            break;
                        case "pose":
                            draft.publish.poseTopic =
                                value ?? DEFAULT_PUBLISH_SETTINGS.poseTopic;
                            break;
                        case "pose_estimate":
                            draft.publish.poseEstimateTopic =
                                value ?? DEFAULT_PUBLISH_SETTINGS.poseEstimateTopic;
                            break;
                    }
                });
            }
            else if (path[1] === "type") {
                // ThreeDeeRender will update the config based on this change
                if (this.renderer.publishClickTool.publishClickType !== value) {
                    this.renderer.publishClickTool.setPublishClickType(value);
                    this.renderer.publishClickTool.stop();
                }
            }
            else {
                this.renderer.updateConfig((draft) => _.set(draft, path, value));
            }
        }
        else {
            return;
        }
        // Update the settings sidebar
        this.updateSettingsTree();
    };
    #handlePublishToolChange = () => {
        this.renderer.updateConfig((draft) => {
            draft.publish.type = this.renderer.publishClickTool.publishClickType;
            return draft;
        });
        this.updateSettingsTree();
    };
}
