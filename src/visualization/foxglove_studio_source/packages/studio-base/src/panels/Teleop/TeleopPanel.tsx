// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/

import * as _ from "lodash-es";
import { useCallback, useEffect, useLayoutEffect, useState } from "react";
import { DeepPartial } from "ts-essentials";

import { ros1 } from "@foxglove/rosmsg-msgs-common";
import {
  PanelExtensionContext,
  SettingsTreeAction,
  SettingsTreeNode,
  SettingsTreeNodes,
  Topic,
} from "@foxglove/studio";
import EmptyState from "@foxglove/studio-base/components/EmptyState";
import Stack from "@foxglove/studio-base/components/Stack";
import ThemeProvider from "@foxglove/studio-base/theme/ThemeProvider";

import DirectionalPad, { DirectionalPadAction } from "./DirectionalPad";

const EMERGENCY_STOP_TOPIC = "/rrc_safety/emergency_stop";
const EMERGENCY_STOP_STATE_TOPIC = "/rrc_safety/emergency_stop_state";
const EMPTY_VARIABLES = new Map<string, unknown>();
type EmergencyStopCommand = "stop" | "release";

type TeleopPanelProps = {
  context: PanelExtensionContext;
};

const geometryMsgOptions = [
  { label: "linear-x", value: "linear-x" },
  { label: "linear-y", value: "linear-y" },
  { label: "linear-z", value: "linear-z" },
  { label: "angular-x", value: "angular-x" },
  { label: "angular-y", value: "angular-y" },
  { label: "angular-z", value: "angular-z" },
];

type Config = {
  topic: undefined | string;
  publishRate: number;
  speedVariableName: undefined | string;
  upButton: { field: string; value: number };
  downButton: { field: string; value: number };
  leftButton: { field: string; value: number };
  rightButton: { field: string; value: number };
};

function buildSettingsTree(config: Config, topics: readonly Topic[]): SettingsTreeNodes {
  const general: SettingsTreeNode = {
    label: "通用",
    fields: {
      publishRate: { label: "发布频率", input: "number", value: config.publishRate },
      topic: {
        label: "话题",
        input: "autocomplete",
        value: config.topic,
        items: topics.map((t) => t.name),
      },
      speedVariableName: {
        label: "前进速度全局变量",
        input: "string",
        value: config.speedVariableName,
      },
    },
    children: {
      upButton: {
        label: "上按钮",
        fields: {
          field: {
            label: "字段",
            input: "select",
            value: config.upButton.field,
            options: geometryMsgOptions,
          },
          value: { label: "值", input: "number", value: config.upButton.value },
        },
      },
      downButton: {
        label: "下按钮",
        fields: {
          field: {
            label: "字段",
            input: "select",
            value: config.downButton.field,
            options: geometryMsgOptions,
          },
          value: { label: "值", input: "number", value: config.downButton.value },
        },
      },
      leftButton: {
        label: "左按钮",
        fields: {
          field: {
            label: "字段",
            input: "select",
            value: config.leftButton.field,
            options: geometryMsgOptions,
          },
          value: { label: "值", input: "number", value: config.leftButton.value },
        },
      },
      rightButton: {
        label: "右按钮",
        fields: {
          field: {
            label: "字段",
            input: "select",
            value: config.rightButton.field,
            options: geometryMsgOptions,
          },
          value: { label: "值", input: "number", value: config.rightButton.value },
        },
      },
    },
  };

  return { general };
}

function TeleopPanel(props: TeleopPanelProps): JSX.Element {
  const { context } = props;
  const { saveState } = context;

  const [currentAction, setCurrentAction] = useState<DirectionalPadAction | undefined>();
  const [emergencyStopped, setEmergencyStopped] = useState(false);
  const [globalVariables, setGlobalVariables] =
    useState<ReadonlyMap<string, unknown>>(EMPTY_VARIABLES);
  const [topics, setTopics] = useState<readonly Topic[]>([]);

  // resolve an initial config which may have some missing fields into a full config
  const [config, setConfig] = useState<Config>(() => {
    const partialConfig = context.initialState as DeepPartial<Config>;

    const {
      topic,
      publishRate = 1,
      speedVariableName,
      upButton: { field: upField = "linear-x", value: upValue = 1 } = {},
      downButton: { field: downField = "linear-x", value: downValue = -1 } = {},
      leftButton: { field: leftField = "angular-z", value: leftValue = 1 } = {},
      rightButton: { field: rightField = "angular-z", value: rightValue = -1 } = {},
    } = partialConfig;

    return {
      topic,
      publishRate,
      speedVariableName,
      upButton: { field: upField, value: upValue },
      downButton: { field: downField, value: downValue },
      leftButton: { field: leftField, value: leftValue },
      rightButton: { field: rightField, value: rightValue },
    };
  });

  const settingsActionHandler = useCallback((action: SettingsTreeAction) => {
    if (action.action !== "update") {
      return;
    }

    setConfig((previous) => {
      const newConfig = { ...previous };
      _.set(newConfig, action.payload.path.slice(1), action.payload.value);
      return newConfig;
    });
  }, []);

  // setup context render handler and render done handling
  const [renderDone, setRenderDone] = useState<() => void>(() => () => {});
  const [colorScheme, setColorScheme] = useState<"dark" | "light">("light");
  useLayoutEffect(() => {
    context.watch("topics");
    context.watch("colorScheme");
    context.watch("currentFrame");
    context.watch("variables");

    context.onRender = (renderState, done) => {
      setTopics(renderState.topics ?? []);
      setGlobalVariables(renderState.variables ?? EMPTY_VARIABLES);
      setRenderDone(() => done);
      if (renderState.colorScheme) {
        setColorScheme(renderState.colorScheme);
      }
      for (const event of renderState.currentFrame ?? []) {
        if (event.topic === EMERGENCY_STOP_STATE_TOPIC) {
          const data = (event.message as { data?: unknown }).data;
          if (typeof data === "boolean") {
            setEmergencyStopped(data);
          }
        }
      }
    };
  }, [context]);

  useEffect(() => {
    context.subscribe([{ topic: EMERGENCY_STOP_STATE_TOPIC, preload: false }]);
    return () => {
      context.unsubscribeAll();
    };
  }, [context]);

  useEffect(() => {
    const tree = buildSettingsTree(config, topics);
    context.updatePanelSettingsEditor({
      actionHandler: settingsActionHandler,
      nodes: tree,
    });
    saveState(config);
  }, [config, context, saveState, settingsActionHandler, topics]);

  // advertise topic
  const { topic: currentTopic } = config;
  useLayoutEffect(() => {
    if (!currentTopic) {
      return;
    }

    context.advertise?.(currentTopic, "geometry_msgs/Twist", {
      datatypes: new Map([
        ["geometry_msgs/Vector3", ros1["geometry_msgs/Vector3"]],
        ["geometry_msgs/Twist", ros1["geometry_msgs/Twist"]],
      ]),
    });

    return () => {
      context.unadvertise?.(currentTopic);
    };
  }, [context, currentTopic]);

  useLayoutEffect(() => {
    context.advertise?.(EMERGENCY_STOP_TOPIC, "std_msgs/Bool", {
      datatypes: new Map([["std_msgs/Bool", ros1["std_msgs/Bool"]]]),
    });

    return () => {
      context.unadvertise?.(EMERGENCY_STOP_TOPIC);
    };
  }, [context]);

  useLayoutEffect(() => {
    if (currentAction == undefined || !currentTopic) {
      return;
    }

    const message = {
      linear: {
        x: 0,
        y: 0,
        z: 0,
      },
      angular: {
        x: 0,
        y: 0,
        z: 0,
      },
    };

    function setFieldValue(field: string, value: number) {
      switch (field) {
        case "linear-x":
          message.linear.x = value;
          break;
        case "linear-y":
          message.linear.y = value;
          break;
        case "linear-z":
          message.linear.z = value;
          break;
        case "angular-x":
          message.angular.x = value;
          break;
        case "angular-y":
          message.angular.y = value;
          break;
        case "angular-z":
          message.angular.z = value;
          break;
      }
    }

    const variableValue = config.speedVariableName
      ? globalVariables.get(config.speedVariableName)
      : undefined;
    const requestedSpeed =
      typeof variableValue === "number" && Number.isFinite(variableValue)
        ? Math.min(1.5, Math.max(0.3, Math.abs(variableValue)))
        : undefined;

    switch (currentAction) {
      case DirectionalPadAction.UP:
        setFieldValue(
          config.upButton.field,
          config.upButton.field === "linear-x" && requestedSpeed != undefined
            ? requestedSpeed
            : config.upButton.value,
        );
        break;
      case DirectionalPadAction.DOWN:
        setFieldValue(
          config.downButton.field,
          config.downButton.field === "linear-x" && requestedSpeed != undefined
            ? -requestedSpeed
            : config.downButton.value,
        );
        break;
      case DirectionalPadAction.LEFT:
        setFieldValue(config.leftButton.field, config.leftButton.value);
        break;
      case DirectionalPadAction.RIGHT:
        setFieldValue(config.rightButton.field, config.rightButton.value);
        break;
      default:
    }

    // don't publish if rate is 0 or negative - this is a config error on user's part
    if (config.publishRate <= 0) {
      return;
    }

    const intervalMs = (1000 * 1) / config.publishRate;
    context.publish?.(currentTopic, message);
    const intervalHandle = setInterval(() => {
      context.publish?.(currentTopic, message);
    }, intervalMs);

    return () => {
      clearInterval(intervalHandle);
    };
  }, [context, config, currentTopic, currentAction, globalVariables]);

  useLayoutEffect(() => {
    renderDone();
  }, [renderDone]);

  const publishEmergencyStop = useCallback(
    (command: EmergencyStopCommand) => {
      const stop = command === "stop";
      setCurrentAction(undefined);
      if (stop && currentTopic) {
        context.publish?.(currentTopic, {
          linear: { x: 0, y: 0, z: 0 },
          angular: { x: 0, y: 0, z: 0 },
        });
      }
      context.publish?.(EMERGENCY_STOP_TOPIC, { data: stop });
      setEmergencyStopped(stop);
    },
    [context, currentTopic],
  );

  const onEmergencyStopClick = useCallback(() => {
    if (!emergencyStopped) {
      publishEmergencyStop("stop");
      return;
    }
    if (window.confirm("确认小车周围安全，并且准备恢复接收速度指令？")) {
      publishEmergencyStop("release");
    }
  }, [emergencyStopped, publishEmergencyStop]);

  const canPublish = context.publish != undefined && config.publishRate > 0;
  const canEmergencyStop = context.publish != undefined;
  const hasTopic = Boolean(currentTopic);
  const movementEnabled = canPublish && hasTopic && !emergencyStopped;

  return (
    <ThemeProvider isDark={colorScheme === "dark"}>
      <Stack
        fullHeight
        justifyContent="center"
        alignItems="center"
        style={{ padding: "min(5%, 8px)", textAlign: "center" }}
      >
        {!canPublish && <EmptyState>请连接支持发布功能的数据源</EmptyState>}
        {canPublish && !hasTopic && <EmptyState>请在面板设置中选择发布话题</EmptyState>}
        {canEmergencyStop && (
          <DirectionalPad
            onAction={setCurrentAction}
            disabled={!movementEnabled}
            emergencyStopped={emergencyStopped}
            onEmergencyStop={onEmergencyStopClick}
          />
        )}
      </Stack>
    </ThemeProvider>
  );
}

export default TeleopPanel;
