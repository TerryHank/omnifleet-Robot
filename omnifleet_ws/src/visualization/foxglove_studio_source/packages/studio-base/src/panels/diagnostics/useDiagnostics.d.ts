import { MessageEvent } from "@foxglove/studio-base/players/types";
import { DiagnosticsById } from "./util";
type UseDiagnosticsResult = Map<string, DiagnosticsById>;
export declare function addMessages(prevResult: UseDiagnosticsResult, msgEvents: readonly MessageEvent[]): UseDiagnosticsResult;
export default function useDiagnostics(topic?: string): UseDiagnosticsResult;
export {};
