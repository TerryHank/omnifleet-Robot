/// <reference types="react" />
import { FzfResultItem } from "fzf";
import { MessagePathSearchItem } from "./getMessagePathSearchItems";
export declare function MessagePathRow({ messagePathResult, style, selected, onClick, onContextMenu, }: {
    messagePathResult: FzfResultItem<MessagePathSearchItem>;
    style: React.CSSProperties;
    selected: boolean;
    onClick: React.MouseEventHandler<HTMLDivElement>;
    onContextMenu: React.MouseEventHandler<HTMLDivElement>;
}): JSX.Element;
