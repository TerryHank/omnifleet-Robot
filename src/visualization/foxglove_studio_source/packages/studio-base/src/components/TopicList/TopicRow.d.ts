/// <reference types="react" />
import { FzfResultItem } from "fzf";
import { Topic } from "@foxglove/studio-base/players/types";
export declare function TopicRow({ topicResult, style, selected, onClick, onContextMenu, }: {
    topicResult: FzfResultItem<Topic>;
    style: React.CSSProperties;
    selected: boolean;
    onClick: React.MouseEventHandler<HTMLDivElement>;
    onContextMenu: React.MouseEventHandler<HTMLDivElement>;
}): JSX.Element;
