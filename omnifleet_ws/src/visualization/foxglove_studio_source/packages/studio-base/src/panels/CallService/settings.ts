// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/

import { produce } from "immer";
import * as _ from "lodash-es";
import { useMemo } from "react";

import { useShallowMemo } from "@foxglove/hooks";
import { SettingsTreeAction, SettingsTreeNodes } from "@foxglove/studio";

import { Config } from "./types";

export const defaultConfig: Config = {
  requestPayload: "{}",
  layout: "vertical",
};

function serviceError(serviceName?: string) {
  if (!serviceName) {
    return "Service cannot be empty";
  }
  return undefined;
}

export function settingsActionReducer(prevConfig: Config, action: SettingsTreeAction): Config {
  return produce(prevConfig, (draft) => {
    if (action.action === "update") {
      const { path, value } = action.payload;
      _.set(draft, path.slice(1), value);
    }
  });
}

export function useSettingsTree(config: Config): SettingsTreeNodes {
  const settings = useMemo(
    (): SettingsTreeNodes => ({
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
    }),
    [config],
  );
  return useShallowMemo(settings);
}
