/// <reference types="react" />
import { DraggingTabItem, TabActions } from "@foxglove/studio-base/panels/Tab/TabDndContext";
import { TabConfig } from "@foxglove/studio-base/types/layouts";
type Props = {
    panelId: string;
    actions: TabActions;
    tabs: TabConfig[];
    activeTabIdx: number;
    setDraggingTabState: (arg0: {
        isOver: boolean;
        item?: DraggingTabItem;
    }) => void;
};
export declare function TabbedToolbar(props: Props): JSX.Element;
export {};
