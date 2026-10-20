import { SettingsTreeNodes } from "@foxglove/studio";
import { DiagnosticStatusConfig, DiagnosticSummaryConfig } from "./util";
export declare function buildSummarySettingsTree(config: DiagnosticSummaryConfig, topicToRender: string, availableTopics: readonly string[]): SettingsTreeNodes;
export declare function buildStatusPanelSettingsTree(config: DiagnosticStatusConfig, topicToRender: string, availableTopics: readonly string[]): SettingsTreeNodes;
