import { LogMessageEvent, NormalizedLogMessage } from "./types";
export declare function getNormalizedMessage(logMessage: Partial<LogMessageEvent["message"]>): string;
export declare function getNormalizedLevel(datatype: string, raw: Partial<LogMessageEvent["message"]>): number;
export declare function normalizedLogMessage(datatype: string, raw: LogMessageEvent["message"]): NormalizedLogMessage;
