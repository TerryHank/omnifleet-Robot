// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/

import * as _ from "lodash-es";

import { filterMap } from "@foxglove/den/collection";
import { SettingsTreeFields, SettingsTreeNodes, Topic } from "@foxglove/studio";

// Persisted panel state
export type Config = {
  center?: { lat: number; lon: number };
  customTileUrl: string;
  disabledTopics: string[];
  followTopic: string;
  layer: string;
  topicColors: Record<string, string>;
  zoomLevel?: number;
  maxNativeZoom?: number;
};

export function validateCustomUrl(url: string): Error | undefined {
  const placeholders = url.match(/\{.+?\}/g) ?? [];
  const validPlaceholders = ["{x}", "{y}", "{z}"];
  for (const placeholder of placeholders) {
    if (!validPlaceholders.includes(placeholder)) {
      return new Error(`Invalid placeholder ${placeholder}`);
    }
  }

  return undefined;
}

function isGeoJSONSchema(schemaName: string) {
  switch (schemaName) {
    case "foxglove_msgs/GeoJSON":
    case "foxglove_msgs/msg/GeoJSON":
    case "foxglove::GeoJSON":
    case "foxglove.GeoJSON":
      return true;
    default:
      return false;
  }
}

export function buildSettingsTree(
  config: Config,
  eligibleTopics: Omit<Topic, "datatype">[],
): SettingsTreeNodes {
  const topics: SettingsTreeNodes = _.transform(
    eligibleTopics,
    (result, topic) => {
      const coloring = config.topicColors[topic.name];
      result[topic.name] = {
        label: topic.name,
        fields: {
          enabled: {
            label: "已启用",
            input: "boolean",
            value: !config.disabledTopics.includes(topic.name),
          },
          coloring: {
            label: "着色",
            input: "select",
            value: coloring ? "Custom" : "Automatic",
            options: [
              { label: "自动", value: "Automatic" },
              { label: "自定义", value: "Custom" },
            ],
          },
          color: coloring
            ? {
                label: "颜色",
                input: "rgb",
                value: coloring,
              }
            : undefined,
        },
      };
    },
    {} as SettingsTreeNodes,
  );

  const eligibleFollowTopicOptions = filterMap(eligibleTopics, (topic) =>
    config.disabledTopics.includes(topic.name) || isGeoJSONSchema(topic.schemaName)
      ? undefined
      : { label: topic.name, value: topic.name },
  );
  const followTopicOptions = [{ label: "关闭", value: "" }, ...eligibleFollowTopicOptions];
  const generalSettings: SettingsTreeFields = {
    layer: {
      label: "地图图层",
      input: "select",
      value: config.layer,
      options: [
        { label: "地图", value: "map" },
        { label: "卫星图", value: "satellite" },
        { label: "自定义", value: "custom" },
      ],
    },
  };

  // Only show the custom url input when the user selects the custom layer
  if (config.layer === "custom") {
    let error: string | undefined;
    if (config.customTileUrl.length > 0) {
      error = validateCustomUrl(config.customTileUrl)?.message;
    }

    generalSettings.customTileUrl = {
      label: "自定义地图瓦片 URL",
      input: "string",
      value: config.customTileUrl,
      error,
    };

    generalSettings.maxNativeZoom = {
      label: "最大瓦片层级",
      input: "select",
      value: config.maxNativeZoom,
      options: [18, 19, 20, 21, 22, 23, 24].map((num) => {
        return { label: String(num), value: num };
      }),
      help: "Highest zoom supported by the custom map source. See https://leafletjs.com/examples/zoom-levels/ for more information.",
    };
  }

  generalSettings.followTopic = {
    label: "跟随话题",
    input: "select",
    value: config.followTopic,
    options: followTopicOptions,
  };

  const settings: SettingsTreeNodes = {
    general: {
      label: "通用",
      fields: generalSettings,
    },
    topics: {
      label: "话题",
      children: topics,
    },
  };

  return settings;
}
