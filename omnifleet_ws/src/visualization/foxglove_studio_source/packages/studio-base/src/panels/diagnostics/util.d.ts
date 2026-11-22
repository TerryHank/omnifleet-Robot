import { Time } from "@foxglove/rostime";
import { Header } from "@foxglove/studio-base/types/Messages";
export declare const MAX_STRING_LENGTH = 5000;
export declare const DEFAULT_SECONDS_UNTIL_STALE = 5;
export declare const LEVELS: {
    OK: 0;
    WARN: 1;
    ERROR: 2;
    STALE: 3;
};
export declare const LEVEL_NAMES: {
    [key: number]: string;
};
export declare const KNOWN_LEVELS: number[];
interface ToString {
    toString(): string;
}
export type DiagnosticStatusConfig = {
    selectedHardwareId?: string;
    selectedName?: string;
    splitFraction?: number;
    topicToRender: string;
    numericPrecision?: number;
    secondsUntilStale?: number;
};
export type DiagnosticSummaryConfig = {
    minLevel: number;
    pinnedIds: DiagnosticId[];
    topicToRender: string;
    hardwareIdFilter: string;
    sortByLevel?: boolean;
    secondsUntilStale?: number;
};
export type DiagnosticId = string & ToString;
export type KeyValue = {
    key: string;
    value: string;
};
export type DiagnosticStatusMessage = {
    name: string;
    hardware_id: string;
    level: number;
    message: string;
    values: KeyValue[];
};
export type DiagnosticInfo = {
    status: DiagnosticStatusMessage;
    stamp: Time;
    id: DiagnosticId;
    displayName: string;
};
export type DiagnosticStatusArrayMsg = {
    header: Header;
    status: DiagnosticStatusMessage[];
};
export type DiagnosticsById = Map<DiagnosticId, DiagnosticInfo>;
export declare function trimHardwareId(hardwareId: string): string;
export declare function getDiagnosticId(hardwareId: string, name?: string): DiagnosticId;
export declare function getDisplayName(hardwareId: string, name: string): string;
export declare function computeDiagnosticInfo(status: DiagnosticStatusMessage, stamp: Time): DiagnosticInfo;
export declare function getDiagnosticsByLevel(diagnosticsByHardwareId: Map<string, DiagnosticsById>): Map<number, DiagnosticInfo[]>;
export declare function getDiagnosticsWithStales(diagnosticsByHardwareId: Map<string, DiagnosticsById>, staleTime: Time): Map<string, DiagnosticsById>;
export declare const filterAndSortDiagnostics: (nodes: DiagnosticInfo[], hardwareIdFilter: string, pinnedIds: DiagnosticId[]) => DiagnosticInfo[];
export {};
