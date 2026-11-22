// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { produce } from "immer";
import * as _ from "lodash-es";
import { useMemo } from "react";
import { useShallowMemo } from "@foxglove/hooks";
export const defaultConfig = {
    requestPayload: "{}",
    layout: "vertical",
};
function serviceError(serviceName) {
    if (!serviceName) {
        return "Service cannot be empty";
    }
    return undefined;
}
export function settingsActionReducer(prevConfig, action) {
    return produce(prevConfig, (draft) => {
        if (action.action === "update") {
            const { path, value } = action.payload;
            _.set(draft, path.slice(1), value);
        }
    });
}
export function useSettingsTree(config) {
    const settings = useMemo(() => ({
        general: {
            fields: {
                serviceName: {
                    label: "服务名称",
                    input: "string",
                    error: serviceError(config.serviceName),
                    value: config.serviceName ?? "",
                },
                layout: {
                    label: "布局",
                    input: "toggle",
                    options: [
                        { label: "垂直", value: "vertical" },
                        { label: "水平", value: "horizontal" },
                    ],
                    value: config.layout ?? defaultConfig.layout,
                },
            },
        },
        button: {
            label: "按钮",
            fields: {
                buttonText: {
                    label: "标题",
                    input: "string",
                    value: config.buttonText,
                    placeholder: `Call service ${config.serviceName ?? ""}`,
                },
                buttonTooltip: { label: "工具提示", input: "string", value: config.buttonTooltip },
                buttonColor: { label: "颜色", input: "rgb", value: config.buttonColor },
            },
        },
    }), [config]);
    return useShallowMemo(settings);
}
