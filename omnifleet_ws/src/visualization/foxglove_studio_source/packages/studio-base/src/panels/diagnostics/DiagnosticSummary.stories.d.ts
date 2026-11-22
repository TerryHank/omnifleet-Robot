import { StoryObj } from "@storybook/react";
import { DiagnosticStatusArrayMsg, KeyValue } from "@foxglove/studio-base/panels/diagnostics/util";
import { MessageEvent } from "@foxglove/studio-base/players/types";
declare const _default: {
    title: string;
    excludeStories: string[];
};
export default _default;
export declare function makeDiagnosticMessage(level: number, name: string, hardware_id: string, messages: string[], options?: {
    values?: KeyValue[] | undefined;
    stamp?: MessageEvent<DiagnosticStatusArrayMsg>["message"]["header"]["stamp"];
}): MessageEvent<DiagnosticStatusArrayMsg>;
export declare const Empty: StoryObj;
export declare const Basic: StoryObj;
export declare const WithSettings: StoryObj;
export declare const WithPinnedNodes: StoryObj;
export declare const WithPinnedNodesAndFilter: StoryObj;
export declare const WithoutSorting: StoryObj;
export declare const FilteredByHardwareId: StoryObj;
export declare const FilteredByLevel: StoryObj;
export declare const FilteredByHardwareIdAndLevel: StoryObj;
export declare const OldDiagnosticsMarkedStale: StoryObj;
