import { SettingsTreeNodes, Topic } from "@foxglove/studio";
export type Config = {
    center?: {
        lat: number;
        lon: number;
    };
    customTileUrl: string;
    disabledTopics: string[];
    followTopic: string;
    layer: string;
    topicColors: Record<string, string>;
    zoomLevel?: number;
    maxNativeZoom?: number;
};
export declare function validateCustomUrl(url: string): Error | undefined;
export declare function buildSettingsTree(config: Config, eligibleTopics: Omit<Topic, "datatype">[]): SettingsTreeNodes;
