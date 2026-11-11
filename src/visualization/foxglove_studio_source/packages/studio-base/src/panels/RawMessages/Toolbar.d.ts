/// <reference types="react" />
import { Topic } from "@foxglove/studio";
import { SaveConfig } from "@foxglove/studio-base/types/panels";
import { RawMessagesPanelConfig } from "./types";
type Props = {
    canExpandAll: boolean;
    diffEnabled: boolean;
    diffMethod: RawMessagesPanelConfig["diffMethod"];
    diffTopicPath: string;
    onDiffTopicPathChange: (path: string) => void;
    onToggleDiff: () => void;
    onToggleExpandAll: () => void;
    onTopicPathChange: (path: string) => void;
    saveConfig: SaveConfig<RawMessagesPanelConfig>;
    topic?: Topic;
    topicPath: string;
};
declare function ToolbarComponent(props: Props): JSX.Element;
export declare const Toolbar: import("react").MemoExoticComponent<typeof ToolbarComponent>;
export {};
