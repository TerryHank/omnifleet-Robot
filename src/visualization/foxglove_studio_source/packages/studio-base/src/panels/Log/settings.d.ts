import { TFunction } from "i18next";
import { SettingsTreeNodes } from "@foxglove/studio";
import { Topic } from "@foxglove/studio-base/players/types";
export declare function buildSettingsTree(topicToRender: string, minLogLevel: number, nameFilter: Record<string, {
    visible?: boolean;
}>, availableTopics: Topic[], availableNames: string[], t: TFunction<"log">): SettingsTreeNodes;
