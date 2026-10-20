export declare enum NodeState {
    Collapsed = "c",
    Expanded = "e"
}
export type NodeExpansion = "all" | "none" | Record<string, NodeState>;
export type RawMessagesPanelConfig = {
    diffEnabled: boolean;
    diffMethod: "custom" | "previous message";
    diffTopicPath: string;
    expansion?: NodeExpansion;
    showFullMessageForDiff: boolean;
    topicPath: string;
    fontSize: number | undefined;
};
export declare const Constants: {
    readonly CUSTOM_METHOD: "custom";
    readonly PREV_MSG_METHOD: "previous message";
    readonly FONT_SIZE_OPTIONS: readonly [8, 9, 10, 11, 12, 14, 16, 18, 24, 30, 36, 48, 60, 72];
};
