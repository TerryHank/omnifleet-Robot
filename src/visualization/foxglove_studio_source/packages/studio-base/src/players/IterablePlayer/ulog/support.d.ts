import { MessageDefinition } from "@foxglove/message-definition";
import { MessageDefinition as ULogMessageDefinition, ULog, LogLevel } from "@foxglove/ulog";
export declare function messageIdToTopic(msgId: number, ulog: ULog): string | undefined;
export declare function messageDefinitionToRos(msgDef: ULogMessageDefinition): MessageDefinition;
export declare function logLevelToRosout(level: LogLevel): number;
