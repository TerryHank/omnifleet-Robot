import { Ref as ReactRef } from "react";
import { TabActions } from "@foxglove/studio-base/panels/Tab/TabDndContext";
type Props = {
    hidden: boolean;
    highlight: "before" | "after" | undefined;
    innerRef?: ReactRef<HTMLDivElement>;
    isActive: boolean;
    isDragging: boolean;
    actions: TabActions;
    tabCount: number;
    tabIndex: number;
    tabTitle?: string;
};
export declare function ToolbarTab(props: Props): JSX.Element;
export {};
